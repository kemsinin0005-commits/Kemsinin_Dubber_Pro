@echo off
title Kemsinin Dubber Pro Desktop Studio
echo =======================================================
echo  Kemsinin Dubber Pro - PyQt5 Desktop Application
echo =======================================================
set PYTHON_CMD=python
if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
)
echo Launching Kemsinin Dubber Pro Studio GUI...
%PYTHON_CMD% KEMSININ_DUBBER_PRO.py
pause
