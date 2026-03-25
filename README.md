# Outbox Worker

`outbox-worker`는 여러 서비스 DB의 outbox 이벤트를 EventBridge로 발행하는 전용 워커입니다.

## Responsibility
- `posts`, `auth`, `events` DB의 outbox row polling
- EventBridge publish
- retry / backoff / failed 상태 전이 관리

## Runtime
- HTTP API는 없고, 단일 worker 프로세스로만 동작합니다
- 이미지 기본 명령은 `publish_outbox_all_databases` 루프 실행입니다
- Kubernetes에서는 Secret key를 환경변수로 직접 주입합니다

## Pipeline
`outbox-worker`는 알림 이벤트 전달의 중간 publish 계층입니다.

1. 도메인 서비스가 로컬 트랜잭션 안에서 `outbox_events` row를 생성합니다.
2. worker가 `OUTBOX_DATABASES`에 정의된 DB alias를 순회합니다.
3. 각 DB에서 `pending` 상태 outbox row를 batch로 읽습니다.
4. payload의 `source`, `detail_type`, `detail` 값을 사용해 EventBridge `PutEvents`를 호출합니다.
5. publish 성공 시 row를 `published`로 전이하고 `published_at`을 기록합니다.
6. publish 실패 시 `attempts`를 증가시키고, 재시도 한도를 넘으면 `failed`로 전이합니다.

이후 downstream 흐름은 아래와 같습니다.
- EventBridge rule
- notifications SQS queue
- notifications consumer
- notifications DynamoDB read model

즉 `outbox-worker`의 성공 기준은 EventBridge publish 성공까지입니다.
SQS rule routing mismatch 같은 downstream 문제는 별도 모니터링과 재처리 전략이 필요합니다.

## Deploy
- Kubernetes 매니페스트
  - [`outbox-worker/deploy/k8s/outbox-worker-env-externalsecret.yaml`](/home/woosupar/stagelog/outbox-worker/deploy/k8s/outbox-worker-env-externalsecret.yaml)
  - [`outbox-worker/deploy/k8s/outbox-worker-serviceaccount.yaml`](/home/woosupar/stagelog/outbox-worker/deploy/k8s/outbox-worker-serviceaccount.yaml)
  - [`outbox-worker/deploy/k8s/outbox-worker-deployment.yaml`](/home/woosupar/stagelog/outbox-worker/deploy/k8s/outbox-worker-deployment.yaml)
- CI/CD workflow
  - [`outbox-worker/.github/workflows/build-and-push.yml`](/home/woosupar/stagelog/outbox-worker/.github/workflows/build-and-push.yml)

배포 흐름은 아래와 같습니다.
- GitHub Actions가 이미지를 빌드해 ECR에 push
- 같은 workflow가 `stagelog-gitops`의 이미지 태그를 갱신
- ArgoCD가 변경된 태그를 감지해 클러스터에 반영

## Configuration
주요 환경변수 예시는 [`outbox-worker/.env.example`](/home/woosupar/stagelog/outbox-worker/.env.example) 에 있습니다.

운영 환경에서는 SSM Parameter Store를 소스 오브 트루스로 사용하고, ExternalSecret이 필요한 키만 Kubernetes Secret으로 동기화합니다.

## Notes
- `default` DB alias는 Django 부팅 안정성을 위해 유지하고, 실제 publish 대상은 `OUTBOX_DATABASES`로 제어합니다.
- EventBridge publish 권한은 전용 IRSA role을 통해 받습니다.
- downstream routing은 EventBridge rule 필터와 함께 맞아야 하므로, `source` 변경 시 infra도 같이 맞춰야 합니다.
- 현재 `source` 값은 각 서비스가 outbox payload에 넣고, worker는 그 값을 그대로 EventBridge `Source`로 사용합니다.
- 따라서 서비스 코드의 `source`와 infra의 EventBridge rule `source` 필터가 어긋나면 이벤트가 SQS에 도달하지 못할 수 있습니다.
