# 로컬 빌드
```bash
docker build -f docker/api/Dockerfile -t stagelog-outbox-worker .
```

# 로컬 실행
```bash
cp .env.example .env
docker run --rm --env-file .env stagelog-outbox-worker
```

# 참고
```text
이미지 기본 명령은 outbox publish loop 실행입니다.
별도의 HTTP 서버는 띄우지 않습니다.
```
