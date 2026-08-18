# Work intake and stakeholder verification

Intake (transcripts, Slack, a domain-expert inbox, prompts) is **not**
the backlog. Promote it. GitHub Issues are the engineering ledger. PRDs
are the product contract. ADRs are decisions that must still bind in a
year. Stakeholders who do not use GitHub check off sandbox drops on an
external ledger (Slack list by default), not GitHub.

Full procedure:
[`rosetta_docs/architecture/sdlc/work-intake-and-ship-verify.md`](https://github.com/Rosetta-Foundation/rosetta_docs/blob/main/architecture/sdlc/work-intake-and-ship-verify.md)

## Ledger vs contract vs decision

| Artifact | Job | When |
| --- | --- | --- |
| Intake | Raw ask | Transcript, Slack, tracker, prompt |
| **GitHub Issue** | Open/closed work | Anything that must not be forgotten |
| **PRD** | What to build / “done” | Feature-sized; input to `decompose` |
| **ADR** | Durable architecture | Auth, composition, data boundaries — not a UI preference |
| **Bug spec** | Same run machine, no PRD | Non-trivial bug |
| **`docs/releases/`** | Delivered + verify list | Every user-facing sandbox drop |
| **Slack Sandbox verify** | Stakeholder check-off | They may have no GitHub. Do not relay. |
| Chronicle | Why we did it and how we got here | Observational memory — not a backlog or work ledger |

Issue routes: `direct` (drop + PR) · `bug-spec` · `plan` (PRD first).
Do not `decompose` until the PRD is Accepted. Do not PRD a same-day
**bundle**.

A **Feedback** tracker is an inbox. **Sandbox verify** is the smoke
ledger. Never mix them. No regulated or sensitive data on either list.

## Delivery + verify (mandatory for user-facing work)

1. PR body `## Release notes` (feeds prod GitHub Release).
2. Dated `docs/releases/YYYY-MM-DD.md`: **Delivered**, **Not verified**,
   **Verified**, **Out**. Slack Status is the live check-off. Promote
   snapshots Verified into git; never delete a line.
3. Upsert the same Not-verified lines to Slack Sandbox verify. New rows
   notify `VERIFY_NOTIFY_CHANNEL_ID` with the list URL and smoke lines.
4. Do **not** arm a laptop Slack watcher. Failed lands as a comment on
   the Ship issue (hosted **Sandbox verify** Action). Do not treat chat
   “they approved” as the check-off.
5. **Slack-linked asks:** if the operator pasted a Slack permalink as
   the request, record it on the GitHub issue Source. After the fix is
   **deployed to SB** (DEV hosts; stakeholders say Sandbox / SB, not
   “dev”), reply **in that same thread** that a new update for the
   issue has been deployed to SB. No `@channel`. Not on push or CI
   green — only `deploy_green` for the SHA that contains the fix.

Promote to prod only after sandbox Verified. Re-smoke prod as new rows.
