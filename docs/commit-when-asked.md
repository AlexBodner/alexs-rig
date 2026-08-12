# Commit when asked

| Rule | Detail |
|------|--------|
| Default | Agent **does not** commit or open PRs unless you ask in this session |
| When asked | Agent may `git commit` (and `gh pr create` if you said so) |
| Before commit | Batch-review: Desktop `+N -M` and/or IDE SCM / Git Tree Compare |
| Secrets | Never commit `.env`, keys, credentials — see [hygiene.md](hygiene.md) |
| Auto-PR | **Forbidden** as a silent habit |

Standing principle: `P-commit` in L0.
