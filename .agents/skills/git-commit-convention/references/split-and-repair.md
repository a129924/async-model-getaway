# Split and repair playbook

## Partial staging

If only part of a file or part of the whole task is staged:

1. describe only the staged subset
2. or stage the remaining semantic unit before drafting the final message

Useful commands:

```bash
git add -p
git restore --staged <path>
git reset
```

## Noise isolation

When business logic is mixed with lockfiles, snapshots, or broad formatter output:

1. unstage the noise
2. commit the business change first
3. commit the noise separately as `chore:` or `style:`

## Amend path

Suggest `git commit --amend` when:

- the last commit only missed one related file
- the footer is missing or incorrect
- the subject has a typo or wrong scope

Do not suggest amend when the new work is semantically separate from the previous commit.
