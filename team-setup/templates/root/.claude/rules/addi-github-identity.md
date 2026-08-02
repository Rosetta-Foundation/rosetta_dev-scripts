# Open git / GitHub work as Addi (GitHub App)

Agent-authored commits, branches, PRs, and issue writes must use the workspace
**Addi** GitHub App identity — not the human operator’s ambient `gh` login.

Humans cannot Approve their own PRs when branch protection / review rules
require a second party. Opening a PR as the human blocks the Approve → merge
machinery (GHA merge-on-approve and `pr-approve-watch`).

## Hard rules

1. **Before** `git push` of a topic branch you intend to PR, and **before**
   `gh pr create` / `gh issue create` / `gh pr comment` (agent-owned), run:

   ```bash
   # Rosetta workspace
   eval "$(bash ~/.config/rosetta/github-app-activate.sh)"
   # Comita workspace
   eval "$(bash ~/.config/comita/github-app-activate.sh)"
   ```

   Pick the activate script for the **org you are pushing to** (Rosetta vs
   Comita). Prefer `ROSETTA_GH_ACTIVATE` / workspace docs when set.

2. **Verify** the token is Addi before creating the PR:

   ```bash
   gh api user --jq .login
   # expect a bot / app login (e.g. rosetta-s-addi-m[bot], addi-m[bot]) — not the human
   ```

   If `gh api user` returns 403 for installation tokens, verify via the PR
   author after create: `gh pr view <n> --json author` must be Addi. If it is
   the human, **close the PR** and recreate under an activated Addi shell.

3. Set commit author/committer from the activate script exports
   (`GIT_AUTHOR_NAME` / `GIT_AUTHOR_EMAIL` / committer) so DCO sign-off is
   Addi’s. Prefer `git commit -s` after activate.

4. **Never** `unset GH_TOKEN` / fall back to ambient human `gh` auth in order
   to “open a docs PR as the user.” Docs and chore PRs are Addi PRs too.

5. If you already opened a PR as the human by mistake: close it with a short
   note, recreate the same changes on a branch pushed with Addi activated, open
   a new PR as Addi, and point the human at the new URL.

## Exceptions (human must explicitly ask)

- The human says to open or push **as themselves** / with their PAT.
- Emergency hotfix they will merge without the Approve-as-second-party flow.
- Read-only `gh` queries where no write identity is required (still prefer
  Activate when about to write).

## Related

- `pr-approve-watch` — human Approves **Addi** PRs; merge as Addi.
- `issue-resolve-watch` — recreate human-authored issues as Addi when asked.
- `no-tool-attribution` — still no “Made with Cursor” footers.
