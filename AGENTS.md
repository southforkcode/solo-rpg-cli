# AGENTS.md - Solo RPG CLI

## Build/Test Commands

- `make test` - Run the behave unit tests

## Development

- Use `uv` for package management
- Use `behave` for feature testing
- Use `ruff` for linting
- Use `mypy` for type checking
- Always make changes in a feature or bug branch. Do not make changes in main branch.
- For bugs, make sure it's reproducible in a test. Fix the bug. Make sure the test succeeds.
- When creating new test cases for bugs, reference the issue id in the test case name. Add comment to test case with link to issue.
- For features, create a new branch. Add one or more test cases for the feature. Make sure the test succeeds.

## Issue Analysis

- When analyzing issues, make sure you understand the issue completely. 
- If you don't understand the issue, ask for clarification.
- If you need more information, ask for clarification.
- If you need more information, ask for clarification.
- Do not fix the issue until you have a plan and have it approved. The plan should be on an issue ticket. Create an issue ticket if you don't have on.


## Testing

- Run `make test` to run the behave unit tests
- Run `python solo_rpg_cli.py <gamedir>` to run the CLI

## Coding Standards

- Use `ruff` for linting
- Use `mypy` for type checking
- Use `behave` for feature testing
- Use `uv` for package management
- Write unit tests for all new code
- Write feature tests for all new requirements
- Use docstrings for all new code
- Use type hints for all new code
- Create a branch for each new feature
- Create a branch for each new bug fix
- Create a branch for each new refactor
- Do not commit to main branch only to feature/bug branch
- Do not automerge branches - wait to be instructed

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

## Documentation

- Keep documentation up to date
- `AGENTS.md` - Keep this file up to date with agentic instructions
- `README.md` - Keep this file up to date with project information
- `doc\user_guide.md` - Keep this file up to date with information for the user
- `doc\developer_guide.md` - Keep this file up to date with information for the developer
- `doc\API.md` - Keep this file up to date with external API information

