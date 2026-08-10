@echo off
title Kemsinin Dubber Pro Desktop Studio
echo =======================================================
echo  Kemsinin Dubber Pro - Desktop Studio Executable
echo =======================================================
if exist KEMSININ_DUBBER_PRO.exe (
    echo Launching KEMSININ_DUBBER_PRO.exe...
    start "" "KEMSININ_DUBBER_PRO.exe"
    exit
)
set PYTHON_CMD=python
if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
)
echo Launching Kemsinin Dubber Pro Studio GUI via Python...
%PYTHON_CMD% KEMSININ_DUBBER_PRO.py
pause
