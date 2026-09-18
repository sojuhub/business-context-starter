# Test results — v0.3.1 copy-first update

## Executed in this environment
- Date: 2026-09-18.
- Environment: Linux, Python 3.13.5.
- Command: `python3 -m unittest discover -s tests -v`.
- Result: **38 tests passed**: 21 retained local bridge tests, 10 retained package-structure checks, 7 new static copy-first/prior-context contract checks.
- Reused bridge helper unchanged from the supplied v0.3 package. SHA-256: `6bd25c587a4b40566d8bc094e34673d5062848f42ca19d44af4bdb27f22bc009`.

## What these results mean
Temporary synthetic file tests cover the bridge's preservation, approved apply, idempotence, stale/conflict rejection and rollback. Structural tests cover package metadata, internal references, notices and selected instruction text. The 7 added tests do NOT execute exports, parse real conversation archives or evaluate an LLM.

## NOT RUN / NOT IMPLEMENTED
- Mac Codex or Claude Code native plugin loading, native imports, `/import` or memory controls.
- ChatGPT/Claude real exports or selected-history business extraction.
- Gmail, Calendar, Instagram, booking or sales authentication and actual reads.
- Model generation, intent classification, claim extraction, policy merge correctness, cross-session reuse or unrelated-work regression in a real agent.
- Beginner usability or public repository/landing-page publication.
- Universal export parser or migration engine: not implemented; the new file specifies a safe procedure using native tools or existing readers.

A source-preservation instruction is not enforcement, a static text check is not behavioral proof, and an available host feature is not verified support on the user's installed Mac version.

## Output
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

----------------------------------------------------------------------
Ran 38 tests in 0.046s

OK
```
