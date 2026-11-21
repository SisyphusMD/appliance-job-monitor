# #18 WIP: Prove required CI checks reject invalid input

- Kind: pull, state: closed, by cody, created 2026-11-17T16:29:29-08:00
- Labels: none; milestone: none
- refs/pull/18/head -> main, merged: False

Disposable hosted failure proof. The issue link is omitted from this description to test the issue-link gate. Close this draft after recording CI. This fixture must never be merged.

## forgejo-actions, 2026-11-17T16:29:41-08:00

<!-- ai-review -->
**AI review** of `b0bf6efcf9`: This is a draft PR explicitly designed as a disposable fixture to verify that the CI gates (Issue link, Secrets, Diff size, Lint) correctly reject invalid input. The intentional corruptions (broken YAML, synthetic secret, 411-line padding) are the point of the PR, not defects. The PR states it must never be merged and should be closed after recording CI results.

### Open

- **F1** (suggestion, `gate_fixture.py:1`) CI gate test fixture has no tracking issue: Rule 1 says 'No work without an issue' and rule 6 requires every PR to name its issue. Even a disposable CI-gate test should have a short issue (e.g. 'Verify required checks reject invalid input') so the CI results are recorded against something and the fixture's purpose is traceable. Add `Closes #n` once the issue exists, or at minimum reference the issue number in the description. This is a suggestion rather than blocking because the PR is a draft that will never merge and the missing link is itself the thing being tested.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICJnYXRlX2ZpeHR1cmUucHkiLCAibGluZSI6IDEsICJzZXZlcml0eSI6ICJzdWdnZXN0aW9uIiwgInN0YXR1cyI6ICJvcGVuIiwgInRpdGxlIjogIkNJIGdhdGUgdGVzdCBmaXh0dXJlIGhhcyBubyB0cmFja2luZyBpc3N1ZSIsICJkZXRhaWwiOiAiUnVsZSAxIHNheXMgJ05vIHdvcmsgd2l0aG91dCBhbiBpc3N1ZScgYW5kIHJ1bGUgNiByZXF1aXJlcyBldmVyeSBQUiB0byBuYW1lIGl0cyBpc3N1ZS4gRXZlbiBhIGRpc3Bvc2FibGUgQ0ktZ2F0ZSB0ZXN0IHNob3VsZCBoYXZlIGEgc2hvcnQgaXNzdWUgKGUuZy4gJ1ZlcmlmeSByZXF1aXJlZCBjaGVja3MgcmVqZWN0IGludmFsaWQgaW5wdXQnKSBzbyB0aGUgQ0kgcmVzdWx0cyBhcmUgcmVjb3JkZWQgYWdhaW5zdCBzb21ldGhpbmcgYW5kIHRoZSBmaXh0dXJlJ3MgcHVycG9zZSBpcyB0cmFjZWFibGUuIEFkZCBgQ2xvc2VzICNuYCBvbmNlIHRoZSBpc3N1ZSBleGlzdHMsIG9yIGF0IG1pbmltdW0gcmVmZXJlbmNlIHRoZSBpc3N1ZSBudW1iZXIgaW4gdGhlIGRlc2NyaXB0aW9uLiBUaGlzIGlzIGEgc3VnZ2VzdGlvbiByYXRoZXIgdGhhbiBibG9ja2luZyBiZWNhdXNlIHRoZSBQUiBpcyBhIGRyYWZ0IHRoYXQgd2lsbCBuZXZlciBtZXJnZSBhbmQgdGhlIG1pc3NpbmcgbGluayBpcyBpdHNlbGYgdGhlIHRoaW5nIGJlaW5nIHRlc3RlZC4iLCAicmVzcG9uc2UiOiAiIn1d -->
