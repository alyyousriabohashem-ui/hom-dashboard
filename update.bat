@echo off
chcp 65001 >nul
rem === عدّل المسار ده لملف الإكسل عندك ===
set XLSX=C:\Users\YOU\Google Drive\hom_Cash_in_with_dashboard.xlsx

python convert.py "%XLSX%" data.json || (echo فشل التحويل & pause & exit /b 1)
git add data.json
git commit -m "update data" >nul 2>&1
git push && echo تم الرفع - الموقع هيتحدث خلال دقيقة
pause
