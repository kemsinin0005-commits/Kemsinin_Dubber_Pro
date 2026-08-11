@echo off
title Push to GitHub - Kemsinin Dubber
echo ========================================================
echo   Pushing Kemsinin Dubber to GitHub Repository
echo   Repo: https://github.com/kemsinin0006-cyber/KEMSININ_DUBBER.git
echo ========================================================
echo.
echo Executing git push...
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo   [SUCCESS] Code pushed to GitHub successfully!
    echo ========================================================
) else (
    echo ========================================================
    echo   [NOTICE] If a browser login window appeared, please complete
    echo   the GitHub sign-in, then run this file again.
    echo ========================================================
)
echo.
pause
