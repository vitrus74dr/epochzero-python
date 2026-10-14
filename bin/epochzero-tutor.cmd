@echo off
rem Windows shim for epochzero-tutor (see bin/epochzero-tutor).
set "EZ_APP=%~dp0.."
if exist "%EZ_APP%\.venv\Scripts\epochzero-tutor.exe" (
    "%EZ_APP%\.venv\Scripts\epochzero-tutor.exe" %*
) else (
    uv run -q --project "%EZ_APP%" epochzero-tutor %*
)
