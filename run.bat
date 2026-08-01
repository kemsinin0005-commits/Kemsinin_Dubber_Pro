@echo off
title Kemsinin Dubber Pro Server
echo =======================================================
echo  Kemsinin Dubber Pro - AI Studio Local Host
echo =======================================================
echo Starting local web server...
start "" "http://localhost:8000"
python server.py
pause
