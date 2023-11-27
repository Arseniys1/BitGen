@echo off

set privatekeeperapitoken=
set timeout=30
set threads=100

IF EXIST ".\venv" (
    echo Use venv python
    .\venv\Scripts\python.exe main.py --proxy0 %privatekeeperapitoken% --timeout %timeout% --threads %threads%
) ELSE (
    echo Use global python
    python.exe main.py --proxy0 %privatekeeperapitoken% --timeout %timeout% --threads %threads%
)

pause