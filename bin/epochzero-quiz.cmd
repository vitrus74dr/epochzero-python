@echo off
rem Windows shim for epochzero-quiz (see bin/epochzero-tutor).
set "EZ_APP=%~dp0.."
if exist "%EZ_APP%\.venv\Scripts\epochzero-quiz.exe" (
    "%EZ_APP%\.venv\Scripts\epochzero-quiz.exe" %*
) else (
    uv run -q --project "%EZ_APP%" epochzero-quiz %*
)
