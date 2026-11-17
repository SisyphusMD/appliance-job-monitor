# #2 docs: send issues and pull requests to Forgejo

- Kind: pull, state: closed, by cody, created 2026-11-16T12:13:01-08:00
- Labels: none; milestone: none
- refs/pull/2/head -> main, merged: True

Forgejo now takes sign-ins with GitHub accounts, so issues and pull requests go there. Until now the README and CONTRIBUTING sent people to GitHub, which is only a read-only mirror.

What the docs now say:
- A new account waits for a maintainer to activate it.
- New accounts can't create repositories, so there are no forks. Pull requests are AGit pushes: `git push origin HEAD:refs/for/main -o topic=…`, made from a Forgejo clone over HTTPS with an access token.
- CI skips AGit pull requests, because the runners are trusted with release credentials (the guard from #3). A maintainer opens the change again from a branch here to run the full suite.

The push syntax was checked on a private repo, where it opened an AGit pull request (flow=1).
