# SecureSoft Repo Rules

This repository is the SecureSoft fork of TrustTunnel client/library code.

## Workflow

1. Check `git status --short --branch` before edits and before commits.
2. Preserve upstream compatibility unless the task is explicitly a fork-only change.
3. Do not stage unrelated Android library changes.
4. Build/test locally before pushing changes consumed by SecureSoft apps.

## Client Contract

- Preserve APIs used by SecureSoft Android and Windows clients.
- Keep two-node failover support compatible with LK bootstrap payloads.
- Do not break existing credentials or runtime config fields while production clients still depend on them.

## Release Rules

- Version any library/runtime artifact consumed by the SecureSoft client.
- Push source before updating dependent app builds.
