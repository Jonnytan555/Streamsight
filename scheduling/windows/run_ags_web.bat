@echo off
:: Agricultural web runner — schedule via Windows Task Scheduler
:: Trigger: every 6 hours
cd /d C:\Python\Streamsight
call C:\Users\Jonat\anaconda3\Scripts\activate.bat
python -m runners.web.ags_web.run >> C:\Python\Streamsight\logs\runners.log 2>&1
