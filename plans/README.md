# `/plans/` — Feature Plan Files

Feature plans created by the **task-decomposer** subagent before multi-commit work begins.

## Layout

```text
plans/
  {feature-name}/        # kebab-case, matches KAN ticket or feature branch
    plan.md              # single plan file per feature
```

## Lifecycle

1. **Create** — invoke task-decomposer with the KAN ticket and context
2. **Review** — resolve clarifications, commit as first commit on the feature branch
3. **Execute** — work the steps in order, update markers: `[ ]` → `[~]` → `[x]`
4. **Handoff** — if session is long, invoke context-keeper with a RESUME BRIEF
5. **Close** — plan stays in repo after PR merges (QA can reference it)
