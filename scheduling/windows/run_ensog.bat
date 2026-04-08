@echo off
:: ENSOG UMM runner — schedule via Windows Task Scheduler
:: Trigger: every 6 hours
cd /d C:\Python\Streamsight
call C:\Users\Jonat\anaconda3\Scripts\activate.bat
python -m runners.db.ensog.run >> C:\Python\Streamsight\logs\runners.log 2>&1
