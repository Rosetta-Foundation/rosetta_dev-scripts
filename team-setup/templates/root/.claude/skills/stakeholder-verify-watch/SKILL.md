---
name: stakeholder-verify-watch
description: >-
  Publish a sandbox drop’s verify list to Slack (stakeholder check-off
  ledger). Slack Status is the live ledger; do not poll Slack from a
  laptop. Use after a live deploy, or when the user asks to publish
  stakeholder verify.
---

# Stakeholder verify (Slack)

**Stakeholders may not have GitHub.** Chronicle is engineering memory;
the analog is the Slack **Sandbox verify** list. They check **Verified**
or **Failed** there. Slack Status is the live check-off. Git
`docs/releases/` is written at **publish** and snapshotted again at
**promote**. Do **not** arm a laptop Slack poller.

Do **not** use a **Feedback** tracker for this — that list is an inbox
of asks, not a smoke ledger. Operator-linked Slack threads get a
separate SB-deploy **thread reply** (`deploy-verify-watch`); that is
not this list and not `@channel`.

Policy:
[work-intake-and-ship-verify](https://github.com/Rosetta-Foundation/rosetta_docs/blob/main/architecture/sdlc/work-intake-and-ship-verify.md).

## When to publish

- After a user-facing sandbox deploy is green (or will be by the time
  smoke starts).
- When opening / pushing a `verify-live` PR that needs stakeholder smoke.
- When the operator says to publish stakeholder verify.

Pair with `deploy-verify-watch` and `pr-approve-watch`. Slack Verified is
**not** GitHub Approve and is **not** promote-to-prod.

## Hard rules

1. No regulated or sensitive data on rows (no customer names, dumps,
   or filenames that could identify a person).
2. Upsert by Item text + Host — do not duplicate rows for the same smoke
   line on the same host.
3. **Do not** start `watch-stakeholder-verify.sh` or any local Slack poll
   loop. Failed rows are commented onto the Ship issue by a hosted
   GitHub Action (`Sandbox verify`) on the product repo.
4. On **Verified**: do nothing in git. Slack already holds it. Promote
   snapshots checkboxes into `docs/releases/`.
5. On **Failed** (from the Ship issue comment): do **not** mark Verified;
   fix / push / republish the row as Not verified. Do not promote.
6. Do not mark Feedback rows Done until the matching verify item is
   Verified on Slack.

## Publish

```bash
# VERIFY_SLACK_LIST_ID must be in the workspace Slack env (create the
# list once). VERIFY_NOTIFY_CHANNEL_ID is the channel to ping.
bash .cursor/skills/stakeholder-verify-watch/scripts/publish-stakeholder-verify.sh \
  --file path/to/docs/releases/2026-08-13.md \
  --ship 123
```

Publish upserts **Not verified** rows, then posts `<!channel>` in
`VERIFY_NOTIFY_CHANNEL_ID` with the list URL and the new smoke lines
when that variable is set. Do not paste the whole dated markdown into
chat. Re-publish is idempotent — already present rows do not ping
again.

If `VERIFY_SLACK_LIST_ID` is unset, publish prints the rows and exits
2. The list is **Sandbox verify** (not Feedback). After create, put
`VERIFY_SLACK_LIST_ID` and `VERIFY_COL_*` (column ids, not display
names) in the workspace Slack env **and** the matching GitHub Actions
variables on the product repo. Host names come from
`VERIFY_SANDBOX_HOSTS` (comma-separated). Do not fall back to pasting
a giant checklist in chat.

## Live status (no watch loop)

```bash
python3 .cursor/skills/stakeholder-verify-watch/scripts/verify_slack.py status
```

Failed notify and promote snapshot are hosted: workflow `Sandbox verify`.
