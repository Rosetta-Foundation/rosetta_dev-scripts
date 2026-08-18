# Stakeholder verify watch (Slack)

When a user-facing sandbox drop is on a live host (or the user asks to
publish stakeholder verify):

- Follow the **`stakeholder-verify-watch`** skill.
- Upsert **Not verified** lines from `docs/releases/YYYY-MM-DD.md` to the
  Slack **Sandbox verify** list (not the Feedback tracker). New rows
  notify `VERIFY_NOTIFY_CHANNEL_ID` with the list URL and smoke lines.
- **Do not** arm a local Slack poller. Slack is the live ledger. Failed
  rows are commented onto the Ship issue by the hosted **Sandbox verify**
  Action. Promote snapshots Verified into git.
- On **Failed** (issue comment): fix / push / republish as Not verified;
  do not promote.
- Stakeholders may have no GitHub. Do **not** ask the operator to relay
  check-offs.
- Slack Verified is **not** GitHub Approve (`pr-approve-watch`).
- When the operator **linked a Slack thread** as the ask, SB deploy
  green also gets a **thread reply** on that message (see
  `deploy-verify-watch`). That is not this list and not `@channel`.
