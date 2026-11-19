# #21 Default blueprint imports to the latest Forgejo release

- Kind: issue, state: open, by cody, created 2026-11-18T06:33:49-08:00
- Labels: status:blocked, type:chore; milestone: none

Use the primary release asset in the install badge, manual import and blueprint source URL. Preserve re-import of the latest stable release.

## cody, 2026-11-18T06:53:21-08:00

The badge, manual URL and blueprint source now agree in the local patch. The latest Forgejo asset matches the bytes of v0.1.1. Both pinned Home Assistant test environments pass all 105 tests and exercise all 60 blueprint branches. The raw public request currently returns HTTP 500. Landing waits for a successful public blueprint import.
