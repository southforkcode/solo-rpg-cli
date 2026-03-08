# AGENTS.md - Solo RPG CLI

## Roles and Responsibilities

- **Software Architect**: Accountable for enforcing Separation of Concerns (Presentation vs. Core Logic vs. Infrastructure). Ban "God Classes". Mandate adherence to SOLID principles (specifically SRP, OCP, DIP). Approve all structural dependency changes.
- **Software Engineer**: Mandated to write modular, decoupled code. Banned from using `Any` type hints—all boundaries must be strictly typed. Must use standard OOP polymorphism. Must implement Dependency Injection instead of hardcoding instances.
- **Quality Engineer**: Accountable for enforcing an 80%+ test coverage floor. Must ensure tests use proper mocking/interfaces rather than brittle I/O interception. Must ensure the CI pipeline completely fails on any test, lint layer, or type checking failure.

## System Architecture Rules

- Presentation logic (REPL) must never contain domain/business logic.
- Core domain logic must never import infrastructure (I/O, database, file system). 
- Feature additions must be registered via decoupled registry patterns, not hardcoded into core execution loops.
## Build/Test Commands

- `make test` (Linux/Mac) or `test.bat` (Windows) - Run both the Python unittests and behave feature tests
- **CRITICAL**: Always keep `Makefile` and `test.bat` exactly in sync. When adding or modifying test commands, update both files correspondingly.

## Development

- Use `uv` for package management
- Use `behave` for feature testing
- Use `ruff` for linting
- Use `mypy` for type checking
- **Code that fails `ruff` or `mypy` is considered broken and will be rejected.** CI/dev workflows must fail on lint/type errors.
- **CRITICAL WORKFLOW RULE: NEVER COMMIT DIRECTLY TO THE `main` BRANCH.**
  1. ALL changes (documentation, code, tests, tooling) MUST be done in a separate branch (`feature/`, `bugfix/`, `docs/`, `chore/`).
  2. You MUST create a Pull Request (PR) for your branch.
  3. You MUST wait for explicit user review, comments, and approval on the PR before proceeding.
  4. You MUST NOT merge the PR yourself unless explicitly instructed by the user after approval.
  5. **No PR can merge if it lowers test coverage or fails to meet the 80%+ coverage floor.**
- For bugs, make sure it's reproducible in a test. Fix the bug. Make sure the test succeeds.
- When creating new test cases for bugs, reference the issue id in the test case name. Add comment to test case with link to issue.
- For features, create a new branch. Add one or more test cases for the feature. Make sure the test succeeds.
- **Code without an accompanying unit test and feature test will be rejected.**
- Update documentation.

## Issue Analysis

- When analyzing issues, make sure you understand the issue completely. 
- If you don't understand the issue, ask for clarification.
- If you need more information, ask for clarification.
- If you need more information, ask for clarification.
- Do not fix the issue until you have a plan and have it approved. The plan should be on an issue ticket. Create an issue ticket if you don't have on.


## Testing

- Run `make test` (Linux/Mac) or `test.bat` (Windows) to run all unit and feature tests
- Run `python solo_rpg_cli.py <gamedir>` to run the CLI

## Coding Standards

- Use `ruff` for linting (Enforced; failures block merge)
- Use `mypy` for type checking (Enforced; failures block merge; `Any` types are banned at boundaries)
- Use `behave` for feature testing
- Use `uv` for package management
- Write unit tests for all new code (Enforced; 80%+ coverage floor required)
- Write feature tests for all new requirements
- Documentation should be updated as necessary as part of code updates.
- Use docstrings for all new code
- Use strict type hints for all new code. **Banned from using `Any` type hints.**
- Implement Dependency Injection instead of hardcoding instances.
- Use standard OOP polymorphism where applicable.
- Create a branch for each new feature
- Create a branch for each new bug fix
- Create a branch for each new refactor
- **Do not commit to the main branch.** Every change must go through a feature, bug, docs, or chore branch.
- Do not automerge branches - wait to be instructed after a Pull Request review.

## Code Review

- Review all PRs for correctness
- Review all PRs for style
- Review all PRs for documentation
- Review all PRs for tests
- Review all PRs for performance
- Review all PRs for security
- Review all PRs for maintainability
- Review all PRs for readability
- Review all PRs for testability
- Review all PRs for reusability
- Review all PRs for extensibility
- Review all PRs for documentation updates

## Documentation

- Keep documentation up to date. New features should include documentation updates.
- `AGENTS.md` - Keep this file up to date with agentic instructions
- `README.md` - Keep this file up to date with project information
- `doc\user_guide.md` - Keep this file up to date with information for the user
- `doc\developer_guide.md` - Keep this file up to date with information for the developer
- `doc\API.md` - Keep this file up to date with external API information

