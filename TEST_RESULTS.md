# Verification report — Business Context Starter v0.3.2

Executed at: 2026-09-18T08:06:19.405438+00:00
Environment: Linux x86_64, Python 3.13.5.

## Result
**60 / 60 local tests passed** using `python -m unittest discover -s tests -v`.
This is NOT a production or end-to-end AI onboarding certification.

| Tests | Count | What actually ran |
|---|---:|---|
| Original bridge regression tests | 21 | Real local filesystem operations |
| New hardening / CLI tests | 7 | Large-file rollback, malformed JSON and real subprocess plan/apply/rollback |
| Existing package and copy-first contract tests | 17 | Static file/metadata/content checks, not model behavior |
| Release manifest tests | 8 | Real local hash allowlist, path/symlink and limited token-pattern checks |
| Remote publication safety tests | 7 | MOCKED GitHub CLI responses; no remote repository created |

The original 38-test suite was rerun unchanged first and passed.
Seven new bridge tests were run before the fix: five failed or errored, two passed.
After the fixes all seven pass. The pre-fix failures were reproduced, not hypothetical.

## Corrected defects
1. Plans/receipts can exceed the instruction-file size because of escaped diffs and
   base64 backups. Previously an approximately 100 KB instruction file could be
   modified successfully but its receipt could not be read for rollback. Metadata
   now has a separate bounded size limit; instruction limits stay bounded.
2. An insertion that would grow an instruction file past its limit is rejected
   before any target write.
3. Non-object JSON states/plans are rejected clearly instead of causing an
   unhandled AttributeError/TypeError. This is local input validation, not a sandbox.

## Publication state
- Connected GitHub account was read as `sojuhub`.
- The session exposed 48 GitHub read/search actions and no repository creation,
  push, file write or workflow-dispatch action.
- Additional plugin discovery returned the same installed GitHub plugin, not an
  additional usable writer.
- The container has git, but no GitHub CLI binary, configured CLI login or standard
  GH_TOKEN/GITHUB_TOKEN environment value. No credentials were requested or printed.
- **Private repository created: NO. Files uploaded: NO. Remote commit: NONE.**
- An allowlisted private-only upload script and GitHub Actions configuration are
  included for execution in an authenticated Mac environment.

## CI and live behavior
Configured, NOT RUN remotely: Ubuntu/macOS, Python 3.10/3.13, read-only permissions.
The workflow checks local code and static contracts; it does not test Mac Codex.
Action refs were read from their first-party GitHub repositories before pinning.

NOT RUN: Mac Codex/Claude plugin loading, actual Gmail/Calendar/Instagram reads,
ChatGPT exports/native memory imports, real LLM output generation, fresh-session
business-policy reuse, beginner usability, provider permission enforcement.
No external messages were sent and no actual company records were used.

## Scope of safety claims
The publication allowlist prevents accidentally including unlisted local files.
The included credential-pattern check is heuristic and is NOT a complete secret,
PII or security audit. Hashes are not a signed release attestation. Local bridge
checks are not a hostile concurrent-writer defense; apply only after review in a
quiescent, approved project.

## Captured local test output
```text
test_claude_supported_without_importing_entire_wiki (test_bridge.BridgeTests.test_claude_supported_without_importing_entire_wiki) ... ok
test_codex_override_is_not_replaced (test_bridge.BridgeTests.test_codex_override_is_not_replaced) ... ok
test_company_mismatch_blocked (test_bridge.BridgeTests.test_company_mismatch_blocked) ... ok
test_foreign_company_bridge_blocked (test_bridge.BridgeTests.test_foreign_company_bridge_blocked) ... ok
test_install_idempotent (test_bridge.BridgeTests.test_install_idempotent) ... ok
test_modified_bridge_not_overwritten (test_bridge.BridgeTests.test_modified_bridge_not_overwritten) ... ok
test_new_target_rollback_never_deletes (test_bridge.BridgeTests.test_new_target_rollback_never_deletes) ... ok
test_no_terminal_newline_roundtrip (test_bridge.BridgeTests.test_no_terminal_newline_roundtrip) ... ok
test_original_mode_preserved (test_bridge.BridgeTests.test_original_mode_preserved) ... ok
test_parent_symlink_blocked (test_bridge.BridgeTests.test_parent_symlink_blocked) ... ok
test_plan_has_no_target_side_effect (test_bridge.BridgeTests.test_plan_has_no_target_side_effect) ... ok
test_plan_tamper_blocked (test_bridge.BridgeTests.test_plan_tamper_blocked) ... ok
test_preserves_existing_text (test_bridge.BridgeTests.test_preserves_existing_text) ... ok
test_private_workspace_inside_project_blocked (test_bridge.BridgeTests.test_private_workspace_inside_project_blocked) ... ok
test_receipt_outside_private_workspace_blocked (test_bridge.BridgeTests.test_receipt_outside_private_workspace_blocked) ... ok
test_refuses_unapproved_apply (test_bridge.BridgeTests.test_refuses_unapproved_apply) ... ok
test_rollback_approval_required (test_bridge.BridgeTests.test_rollback_approval_required) ... ok
test_rollback_byte_exact (test_bridge.BridgeTests.test_rollback_byte_exact) ... ok
test_rollback_preserves_later_edits (test_bridge.BridgeTests.test_rollback_preserves_later_edits) ... ok
test_stale_plan_refused (test_bridge.BridgeTests.test_stale_plan_refused) ... ok
test_target_symlink_blocked (test_bridge.BridgeTests.test_target_symlink_blocked) ... ok
test_cli_apply_requires_approval (test_bridge_hardening.HardeningTests.test_cli_apply_requires_approval) ... ok
test_cli_plan_apply_rollback_round_trip (test_bridge_hardening.HardeningTests.test_cli_plan_apply_rollback_round_trip) ... ok
test_cli_rejects_non_object_plan_without_traceback (test_bridge_hardening.HardeningTests.test_cli_rejects_non_object_plan_without_traceback) ... ok
test_final_instruction_size_is_checked_before_plan (test_bridge_hardening.HardeningTests.test_final_instruction_size_is_checked_before_plan) ... ok
test_large_instruction_receipt_can_be_rolled_back (test_bridge_hardening.HardeningTests.test_large_instruction_receipt_can_be_rolled_back) ... ok
test_large_plan_cli_round_trip (test_bridge_hardening.HardeningTests.test_large_plan_cli_round_trip) ... ok
test_state_must_be_json_object (test_bridge_hardening.HardeningTests.test_state_must_be_json_object) ... ok
test_entry_is_copy_first (test_copy_first.CopyFirstContractTests.test_entry_is_copy_first) ... ok
test_native_memory_boundaries_present (test_copy_first.CopyFirstContractTests.test_native_memory_boundaries_present) ... ok
test_no_fake_remote_url_in_copy_prompt (test_copy_first.CopyFirstContractTests.test_no_fake_remote_url_in_copy_prompt) ... ok
test_prior_context_reference_is_linked (test_copy_first.CopyFirstContractTests.test_prior_context_reference_is_linked) ... ok
test_provenance_and_repeat_import_contract (test_copy_first.CopyFirstContractTests.test_provenance_and_repeat_import_contract) ... ok
test_release_requires_real_pinned_source (test_copy_first.CopyFirstContractTests.test_release_requires_real_pinned_source) ... ok
test_start_uses_existing_skill (test_copy_first.CopyFirstContractTests.test_start_uses_existing_skill) ... ok
test_all_json_parse (test_package.PackageTests.test_all_json_parse) ... ok
test_brief_and_start_exist (test_package.PackageTests.test_brief_and_start_exist) ... ok
test_exactly_two_internal_skills (test_package.PackageTests.test_exactly_two_internal_skills) ... ok
test_host_manifests_share_identity (test_package.PackageTests.test_host_manifests_share_identity) ... ok
test_marketplace_points_inside_repo (test_package.PackageTests.test_marketplace_points_inside_repo) ... ok
test_no_default_hooks_or_bundled_connections (test_package.PackageTests.test_no_default_hooks_or_bundled_connections) ... ok
test_notices_present_in_installed_package (test_package.PackageTests.test_notices_present_in_installed_package) ... ok
test_portable_manifest_minimal_contract (test_package.PackageTests.test_portable_manifest_minimal_contract) ... ok
test_skill_links_are_internal_and_resolve (test_package.PackageTests.test_skill_links_are_internal_and_resolve) ... ok
test_status_and_onboarding_bounds_visible (test_package.PackageTests.test_status_and_onboarding_bounds_visible) ... ok
test_changed_file_is_rejected (test_publish_private.ManifestTests.test_changed_file_is_rejected) ... ok
test_duplicate_is_rejected (test_publish_private.ManifestTests.test_duplicate_is_rejected) ... ok
test_environment_file_is_rejected (test_publish_private.ManifestTests.test_environment_file_is_rejected) ... ok
test_obvious_token_is_rejected (test_publish_private.ManifestTests.test_obvious_token_is_rejected) ... ok
test_symlink_is_rejected (test_publish_private.ManifestTests.test_symlink_is_rejected) ... ok
test_traversal_is_rejected (test_publish_private.ManifestTests.test_traversal_is_rejected) ... ok
test_unlisted_private_file_is_not_selected (test_publish_private.ManifestTests.test_unlisted_private_file_is_not_selected) ... ok
test_valid_manifest (test_publish_private.ManifestTests.test_valid_manifest) ... ok
test_creates_private_and_verifies_before_push (test_publish_private.RemoteSafetyTests.test_creates_private_and_verifies_before_push) ... ok
test_existing_name_does_not_get_overwritten (test_publish_private.RemoteSafetyTests.test_existing_name_does_not_get_overwritten) ... ok
test_false_like_private_is_rejected (test_publish_private.RemoteSafetyTests.test_false_like_private_is_rejected) ... ok
test_public_remote_blocks_push (test_publish_private.RemoteSafetyTests.test_public_remote_blocks_push) ... ok
test_remote_commit_mismatch_is_not_success (test_publish_private.RemoteSafetyTests.test_remote_commit_mismatch_is_not_success) ... ok
test_remote_identity_mismatch_is_rejected (test_publish_private.RemoteSafetyTests.test_remote_identity_mismatch_is_rejected) ... ok
test_wrong_account_has_no_side_effects (test_publish_private.RemoteSafetyTests.test_wrong_account_has_no_side_effects) ... ok

----------------------------------------------------------------------
Ran 60 tests in 5.294s

OK
```
