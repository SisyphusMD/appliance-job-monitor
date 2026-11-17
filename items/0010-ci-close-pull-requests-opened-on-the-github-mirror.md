# #10 ci: close pull requests opened on the GitHub mirror

- Kind: pull, state: closed, by cody, created 2026-11-17T12:30:40-08:00
- Labels: none; milestone: none
- refs/pull/10/head -> main, merged: True

Closes #11

Part of the adoption, #5.

GitHub cannot turn pull requests off, so the read-only GitHub copy still takes them. `.github/workflows/mirror-lockdown.yml` closes and locks a new one with a pointer to this repo on Forgejo. It is a byte-identical copy of project-rules' file at bef02c1 (merged as SisyphusMD/project-rules#89, and proven there: a test PR on the GitHub copy was closed and locked within seconds). It runs only on GitHub under SisyphusMD, with only `pull-requests: write`, and runs no code from the PR. Issues are already off on the GitHub copy.

Renovate leaves it alone like the other copied workflows; it changes only by copying again. After merge, Actions goes on for the GitHub copy, limited to this one action, SHA-pinned, with a read-only default token.

No tests: a copied workflow, tested in project-rules (`tests/test_mirror_lockdown.py`).

Adoption proof (#5): this PR was opened without an issue link first, and `CI / Issue link (pull_request_target)` failed on it; this edit adds the link. The AI review then held the PR to rule 6's `Closes #n` form, so it closes #11, the lockdown's own issue, and #5 stays open until main is protected.


## forgejo-actions, 2026-11-17T12:32:01-08:00

<!-- ai-review -->
**AI review** of `263f80e9bc`: Clean, well-scoped PR adding a proven byte-identical copy of project-rules' mirror-lockdown workflow, with the necessary Renovate exclusion and changelog entry. No blocking issues found.

### Withdrawn

- **F1** (blocking, `.github/workflows/mirror-lockdown.yml:1`) PR description uses 'Refs #5' instead of 'Closes #5' (rule 6): The current description reads 'Closes #11' and 'Part of the adoption, #5.' Issue #11 is the specific issue this PR addresses; #5 is the umbrella adoption issue that stays open until other work lands. Rule 6 requires the PR to name its issue with 'Closes #n', and it does: 'Closes #11'. The 'Part of the adoption, #5' line is context, not a substitute for the closing keyword. The finding was based on a 'Refs #5' string that does not appear in the current description.
  - Reviewer: Withdrawing: the description correctly uses 'Closes #11' for the issue this PR resolves. #5 is referenced as parent context, which is fine.

### Resolved

- **F2** (suggestion, `.github/workflows/mirror-lockdown.yml:1`) PR description does not follow rule 9 format: 


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICIuZ2l0aHViL3dvcmtmbG93cy9taXJyb3ItbG9ja2Rvd24ueW1sIiwgImxpbmUiOiAxLCAic2V2ZXJpdHkiOiAiYmxvY2tpbmciLCAic3RhdHVzIjogIndpdGhkcmF3biIsICJ0aXRsZSI6ICJQUiBkZXNjcmlwdGlvbiB1c2VzICdSZWZzICM1JyBpbnN0ZWFkIG9mICdDbG9zZXMgIzUnIChydWxlIDYpIiwgImRldGFpbCI6ICJUaGUgY3VycmVudCBkZXNjcmlwdGlvbiByZWFkcyAnQ2xvc2VzICMxMScgYW5kICdQYXJ0IG9mIHRoZSBhZG9wdGlvbiwgIzUuJyBJc3N1ZSAjMTEgaXMgdGhlIHNwZWNpZmljIGlzc3VlIHRoaXMgUFIgYWRkcmVzc2VzOyAjNSBpcyB0aGUgdW1icmVsbGEgYWRvcHRpb24gaXNzdWUgdGhhdCBzdGF5cyBvcGVuIHVudGlsIG90aGVyIHdvcmsgbGFuZHMuIFJ1bGUgNiByZXF1aXJlcyB0aGUgUFIgdG8gbmFtZSBpdHMgaXNzdWUgd2l0aCAnQ2xvc2VzICNuJywgYW5kIGl0IGRvZXM6ICdDbG9zZXMgIzExJy4gVGhlICdQYXJ0IG9mIHRoZSBhZG9wdGlvbiwgIzUnIGxpbmUgaXMgY29udGV4dCwgbm90IGEgc3Vic3RpdHV0ZSBmb3IgdGhlIGNsb3Npbmcga2V5d29yZC4gVGhlIGZpbmRpbmcgd2FzIGJhc2VkIG9uIGEgJ1JlZnMgIzUnIHN0cmluZyB0aGF0IGRvZXMgbm90IGFwcGVhciBpbiB0aGUgY3VycmVudCBkZXNjcmlwdGlvbi4iLCAicmVzcG9uc2UiOiAiV2l0aGRyYXdpbmc6IHRoZSBkZXNjcmlwdGlvbiBjb3JyZWN0bHkgdXNlcyAnQ2xvc2VzICMxMScgZm9yIHRoZSBpc3N1ZSB0aGlzIFBSIHJlc29sdmVzLiAjNSBpcyByZWZlcmVuY2VkIGFzIHBhcmVudCBjb250ZXh0LCB3aGljaCBpcyBmaW5lLiJ9LCB7ImlkIjogIkYyIiwgImZpbGUiOiAiLmdpdGh1Yi93b3JrZmxvd3MvbWlycm9yLWxvY2tkb3duLnltbCIsICJsaW5lIjogMSwgInNldmVyaXR5IjogInN1Z2dlc3Rpb24iLCAic3RhdHVzIjogInJlc29sdmVkIiwgInRpdGxlIjogIlBSIGRlc2NyaXB0aW9uIGRvZXMgbm90IGZvbGxvdyBydWxlIDkgZm9ybWF0IiwgImRldGFpbCI6ICIiLCAicmVzcG9uc2UiOiAiIn1d -->
