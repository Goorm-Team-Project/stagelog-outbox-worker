# outbox-worker

## Responsibility
- Single outbox publisher worker across multiple DB aliases.

## Owned Domain
- No business domain ownership.
- Operational ownership of outbox publish loop only.

## Behavior
- Polls `outbox_events` from multiple DB aliases (`posts_db,auth_db,events_db`)
- Publishes to EventBridge
- Handles retry/backoff and failed state transitions

## Dependencies
- Shared event contract compatibility
- AWS EventBridge access
- DB read/write access to outbox tables

## Runtime
- One worker deployment in EKS
- Image default command runs `python manage.py publish_outbox_all_databases` in a loop
- No HTTP service or ingress is deployed for this repository
