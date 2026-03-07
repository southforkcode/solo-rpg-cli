@echo off
echo Running Ruff validation...
uv run ruff check .
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

echo.
echo Running Mypy type validation...
uv run mypy .
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

echo.
echo Running Python unittests...
uv run python -m unittest discover test/unit
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

echo.
echo Running Behave feature tests...
uv run behave test/features
