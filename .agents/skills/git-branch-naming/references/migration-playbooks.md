# Migration playbooks

## Wrong branch with uncommitted changes

If the user started on `main` or another wrong branch but has not committed yet:

```bash
git checkout -b <correct-branch-name>
```

The working tree changes come along to the new branch.

## Wrong branch name but right task

If the branch already represents the right task and only the name is wrong:

```bash
git branch -m <correct-branch-name>
```

## Wrong branch and wrong task shape

If the branch name hides multiple semantic tasks:

1. choose the first true task branch
2. move only the matching work there
3. keep the remaining work for a second branch

When needed, combine this skill with commit-splitting advice from `git-commit-convention`.
