@echo off
cd %~dp0..
set PYTHONPATH=%CD%
python scripts/deepresearch.py %* 