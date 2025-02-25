@echo off
cd %~dp0..
set PYTHONPATH=%CD%
python backend/main.py 