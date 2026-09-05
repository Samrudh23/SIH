# Contributing to SIH26034

Thank you for contributing to the **SIH26034 Packaged Commodity Compliance System**.

This document defines how the six-member team develops, reviews, tests, and integrates work into the project.

The project uses a **branch-per-member workflow with Pull Request-based integration**.

---

# 1. Core Principle

> `**main**` **is the stable source of truth.**

No member should directly push development work to `main`.

All development takes place on the member's assigned branch and reaches `main` only after review.

---

# 2. Branch Structure

The repository uses the following primary branches:

```
main
├── p1
├── p2
├── p3
├── p4
├── p5
└── p6
```

## Branch ownership

|Branch|Member|Responsibility|
|---|---|---|
|`p1`|P1|AI / OCR / Computer Vision|
|`p2`|P2|Compliance / Rules Engine|
|`p3`|P3|Backend / Database / APIs|
|`p4`|P4|Frontend / UX|
|`p5`|P5|Dashboard / Reports|
|`p6`|P6|QA / Data / Integration|

Each member is primarily responsible for maintaining the quality of their own branch.

---

# 3. `main` Branch Rules

`main` must remain the **latest stable and reviewed version** of the project.

### Do not:

- Push directly to `main`.
    
- Force-push to `main`.
    
- Merge unreviewed work.
    
- Merge knowingly broken code.
    
- Commit secrets.
    
- Commit unrelated experimental code.
    
- Bypass the Pull Request process.
    

### Do:

- Keep `main` runnable.
    
- Merge only reviewed work.
    
- Test changes before merging.
    
- Resolve conflicts carefully.
    
- Keep documentation synchronized with major changes.
    

---

# 4. Standard Development Workflow

Every task should follow this general workflow:

```
1. Understand the task
        ↓
2. Confirm requirements / expected behaviour
        ↓
3. Work on assigned branch
        ↓
4. Implement
        ↓
5. Test locally
        ↓
6. Review your own changes
        ↓
7. Commit
        ↓
8. Push branch
        ↓
9. Open Pull Request
        ↓
10. Code review
        ↓
11. QA / integration check
        ↓
12. Team lead approval
        ↓
13. Merge into main
```

---

# 5. Before Starting Work

Before implementing a task:

### Check:

- What requirement does this implement?
    
- Which phase does it belong to?
    
- Who owns the relevant component?
    
- Does it depend on another member's work?
    
- Does the API/data structure already exist?
    
- Is the expected behaviour documented?
    

If the task is unclear, **ask before building**.

Do not use AI to fill in major project assumptions without checking with the relevant owner.

---

# 6. Working on Your Branch

Members should work on their assigned branch:

```
P1 → p1
P2 → p2
P3 → p3
P4 → p4
P5 → p5
P6 → p6
```

Before beginning substantial work, make sure your branch is reasonably up to date with `main`.

Avoid allowing your branch to remain disconnected from `main` for long periods.

---

# 7. Commit Guidelines

Commits should describe the change clearly.

Use short, meaningful commit messages.

### Recommended format

```
type: short description
```

### Common types

```
feat:
fix:
docs:
test:
refactor:
chore:
```

### Examples

```
feat: add package image upload
feat: implement declaration extraction
feat: add MRP validation rule
fix: handle failed OCR response
test: add net quantity validation cases
docs: update compliance requirements
refactor: simplify inspection service
chore: update project configuration
```

### Avoid

```
update
changes
final
final final
working
stuff
asdf
```

Commit messages should help another developer understand the history months later.

---

# 8. Keep Commits Focused

Prefer several logical commits over one enormous commit.

### Good

```
feat: add inspection image model
feat: add image upload endpoint
test: add inspection image tests
```

### Avoid

```
feat: completely build the entire backend
```

A commit should ideally represent one coherent change.

---

# 9. Pull Requests

When your work is ready:

```
your branch
    ↓
Pull Request
    ↓
main
```

The Pull Request title should clearly describe the work.

### Example

```
feat: implement package OCR pipeline
```

---

# 10. Pull Request Description

Every PR should explain:

```
## What changed?

Describe the implementation.

## Why?

Explain which requirement/problem this addresses.

## Testing

Explain what was tested.

## Known limitations

Mention anything incomplete or unreliable.

## Screenshots

Include screenshots for UI changes where useful.
```

The PR should make it possible for a reviewer to understand the change without opening every file first.

---

# 11. PR Checklist

Before opening a Pull Request:

- The change implements a defined requirement/task.
    
- I understand the code I am submitting.
    
- I tested the change locally.
    
- Existing functionality still works.
    
- No unnecessary files are included.
    
- No secrets/API keys/passwords are included.
    
- No `.env` file is committed.
    
- No unrelated changes are included.
    
- Documentation has been updated if necessary.
    
- UI changes include screenshots where appropriate.
    
- Known limitations are mentioned.
    

---

# 12. Code Review

Code review is a **required part of development**, not a formality.

Reviewers should check:

### Correctness

- Does it actually solve the intended problem?
    
- Does it handle expected edge cases?
    

### Integration

- Does it work with existing APIs/data structures?
    
- Could it break another component?
    

### Security

- Are secrets exposed?
    
- Is user input handled safely?
    
- Are permissions respected?
    

### Maintainability

- Is the code understandable?
    
- Are unnecessary dependencies introduced?
    
- Is there duplicated logic?
    

### Testing

- Has the feature actually been tested?
    

---

# 13. AI / Vibe Coding Rules

AI coding tools are encouraged and may be used extensively.

However:

> **The developer is responsible for the code, regardless of whether it was written manually or generated by AI.**

Before submitting AI-generated code, the developer must:

1. Understand what the code does.
    
2. Check its dependencies.
    
3. Test it.
    
4. Review for security issues.
    
5. Check that it follows the project architecture.
    
6. Remove unnecessary generated code.
    
7. Confirm that it does not conflict with other components.
    

### Do not blindly accept AI suggestions.

In particular, AI must not be trusted to invent:

- Legal requirements
    
- API contracts
    
- Security decisions
    
- Compliance rules
    
- Database structures
    
- Architectural decisions
    

These should be verified with the relevant project documentation and team members.

---

# 14. Legal / Compliance Code

The compliance component requires additional care.

Any implementation based on the Legal Metrology (Packaged Commodities) Rules, 2011 should be traceable to the relevant verified source material.

Do not implement a legal rule solely because:

> "the AI said this is required."

The compliance team should maintain the authoritative mapping between:

```
Legal Requirement
        ↓
Structured Rule
        ↓
Validation Logic
        ↓
System Finding
```

---

# 15. Working Across Team Boundaries

Some features will involve multiple members.

For example:

```
P1 AI
   ↓
P3 Backend
   ↓
P4 Frontend
```

In such cases, agree on the interface **before implementation**.

For example, if P1 produces extracted declarations, the expected structure should be agreed upon before P3 builds around it.

Avoid situations where:

```
P1 builds output A
P3 expects output B
P4 expects output C
```

The relevant API/data contract should be documented first.

---

# 16. Dependencies Between Branches

A member should not permanently depend on another member's unmerged local changes.

If work depends on a feature that is not yet in `main`:

1. Discuss the dependency.
    
2. Agree on the interface.
    
3. Use a temporary mock/stub where practical.
    
4. Integrate once the dependency is merged.
    

This allows team members to continue working independently.

---

# 17. Testing Requirements

Every feature should have an appropriate level of testing.

### Examples

#### AI/OCR

- Different image qualities
    
- Different package layouts
    
- Missing text
    
- Blurry text
    
- Incorrect OCR
    
- Multiple declarations
    

#### Compliance

- Valid declaration
    
- Missing declaration
    
- Invalid declaration
    
- Unclear result
    
- Not-applicable requirement
    

#### Backend

- Valid requests
    
- Invalid requests
    
- Missing fields
    
- Authentication
    
- Error handling
    

#### Frontend

- Upload flow
    
- Loading states
    
- Error states
    
- Empty states
    
- Results display
    
- Mobile/responsive behaviour
    

#### Integration

- Complete inspection workflow
    
- Image → OCR → compliance → result
    
- Evidence generation
    
- Report generation
    
- Database persistence
    

---

# 18. Do Not Commit Secrets

Never commit:

```
API keys
Access tokens
Passwords
Private keys
Database credentials
.env
Service-account credentials
```

Use environment variables.

The repository may contain:

```
.env.example
```

with placeholder values.

It must not contain:

```
.env
```

---

# 19. Dependencies

Before adding a new dependency:

- Confirm it is actually needed.
    
- Check whether an existing dependency already solves the problem.
    
- Understand its purpose.
    
- Avoid adding libraries simply because an AI suggested them.
    

Large or unnecessary dependency additions should be discussed with the relevant owner.

---

# 20. Generated / Temporary Files

Do not commit:

```
node_modules/
.venv/
__pycache__/
dist/
build/
temporary OCR outputs
local logs
IDE configuration
large temporary datasets
```

unless a particular file is intentionally part of the project.

---

# 21. Dataset Guidelines

Package images and test data should be handled carefully.

Do not blindly commit a large dataset to the repository.

For each dataset used for testing, document:

- Source
    
- Purpose
    
- Expected format
    
- Licensing/usage considerations
    
- Ground-truth information where available
    

The QA/Data owner is responsible for coordinating dataset usage.

---

# 22. Documentation

If a change significantly affects:

- Architecture
    
- API
    
- Database
    
- Compliance logic
    
- AI pipeline
    
- User workflow
    

update the relevant documentation.

Documentation should not be treated as something to do only at the end of the project.

---

# 23. Merge Responsibility

The general integration flow is:

```
Developer
    ↓
Pull Request
    ↓
Technical Review
    ↓
P6 QA / Integration Check
    ↓
Team Lead Approval
    ↓
Merge → main
```

The exact reviewer may vary depending on the component.

### Suggested review ownership

|   |   |
|---|---|
|Component|Primary reviewer(s)|
|AI / OCR|P3 + P6|
|Compliance|P2 + P6 / Team Lead|
|Backend|P3 + relevant owner|
|Frontend|P4/P5 + P6|
|Dashboard|P5 + P3/P6|
|QA / Testing|P6 + relevant component owner|

The Team Lead has final merge authority for significant changes.

---

# 24. Merge Conflicts

If a conflict occurs:

**Do not blindly accept one side.**

First determine:

- What changed?
    
- Why did each side change it?
    
- Which version matches the current architecture?
    
- Does the conflict affect another component?
    

When unsure, ask the relevant owner before resolving it.

---

# 25. Branch Hygiene

Keep branches clean.

Do not push:

- unrelated experiments
    
- debug files
    
- API keys
    
- giant generated files
    
- abandoned experiments
    
- code that you know is broken
    

If you are experimenting, use a clearly identified temporary branch or local workspace.

---

# 26. Definition of Done

A feature is considered complete when:

```
Requirement understood
        ↓
Implementation complete
        ↓
Locally tested
        ↓
Edge cases considered
        ↓
Documentation updated if needed
        ↓
PR created
        ↓
Review completed
        ↓
QA/integration completed where required
        ↓
Approved
        ↓
Merged into main
```

**"The AI generated the code" is not the definition of done.**

---

# 27. Project Philosophy

The project should follow these principles:

### Build the core workflow first

```
Image
 ↓
OCR
 ↓
Extraction
 ↓
Rules
 ↓
Finding
 ↓
Evidence
 ↓
Verification
 ↓
Report
```

### Prefer working software over excessive features.

### Prefer simple architecture over unnecessary complexity.

### Keep AI explainable enough for an inspector to understand why something was flagged.

### Keep legal logic separate from AI inference.

### Treat `main` as production-quality relative to the current prototype stage.

### Document important decisions.

---

# 28. Final Rule

> **If you are unsure whether a change should be made, stop and discuss it before coding around the uncertainty.**

A few minutes of coordination is cheaper than six AI coding agents building incompatible versions of the same system.