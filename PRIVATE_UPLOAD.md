# Upload this tested pilot to a new PRIVATE GitHub repository

## Current state
The package has NOT been uploaded in this ChatGPT session. Connected GitHub reads
confirmed the account `sojuhub`, but no write/create action was exposed. No `gh`
binary or GitHub CLI authentication was available in the execution container.

## Mac Codex: copy this prompt
Open this extracted folder in Mac Codex, then paste:

```text
Use this existing Business Context Starter package. Do not rebuild the app.
Read PRIVATE_UPLOAD.md and TEST_RESULTS.md. Run the local tests and inspect
scripts/publish_private.py. Validate RELEASE_MANIFEST.json; never upload
unlisted files, business data, exports, tokens or unrelated projects.

Use the existing GitHub CLI authentication, or guide me through native browser
login if required. Never ask me to paste a token into chat. Confirm the active
account is sojuhub. I authorize creating a NEW PRIVATE repository named
business-context-starter under sojuhub and pushing this reviewed package.
Run python3 scripts/publish_private.py --owner sojuhub --repo business-context-starter --publish.

Stop if that repository already exists; do not overwrite it, delete it, change
its visibility or force push. Do not create a public repository, release or site.
After the script succeeds, verify the private flag and remote commit again.
Inspect the resulting GitHub Actions run; report passed, failed or not-run
accurately. Do not count CI as Mac Codex or live-account behavioral testing.
Give me the real repository URL, commit and test status.
```

## Commands for an already authenticated machine
Python 3.10+, Git, and GitHub CLI (`gh`) are required. Use `gh auth login` locally
when needed. No credential belongs in these files or in the ChatGPT conversation.

```sh
# Default mode performs local checks only; it does not contact GitHub.
python3 scripts/publish_private.py

# Explicit remote action: NEW repository, PRIVATE only.
python3 scripts/publish_private.py --owner sojuhub --repo business-context-starter --publish
```

The uploader uses a separate local snapshot containing only the reviewed manifest
files, creates a local commit there, creates the private remote WITHOUT pushing,
verifies privacy, pushes without force, then compares the remote SHA to the local
commit. It prints the actual URL and local checkout path only after verification.
It does not edit global Git credentials or configuration. Extra local files are
not selected. The limited credential-pattern check is not a full security audit.

The release manifest protects against accidental file changes and extra files;
it is NOT a signed supply-chain attestation. After an intentional source edit,
review it and regenerate the manifest before publishing. Future normal CI does
not enforce the delivery manifest; it runs the regression suite.

Creation errors abort. A failure AFTER creation can leave a new private repository;
inspect it before retrying. The script never deletes or reuses it automatically.
Actions may be disabled by account policy, and may consume included CI minutes.
The workflow uses read-only repository permissions and no account secrets.

## Verified command references
- https://cli.github.com/manual/gh_repo_create
- https://cli.github.com/manual/gh_repo_view
