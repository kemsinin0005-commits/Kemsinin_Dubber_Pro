@echo off
title Push to GitHub - Kemsinin Dubber
echo ========================================================
echo   Pushing Kemsinin Dubber to GitHub Repository
echo   Repo: https://github.com/kemsinin0005-commits/Kemsinin_Dubber_Pro.git
echo ========================================================
echo.
echo Executing git push...
git remote set-url origin https://github.com/kemsinin0005-commits/Kemsinin_Dubber_Pro.git
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
