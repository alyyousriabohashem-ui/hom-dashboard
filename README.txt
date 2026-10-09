داشبورد هوم + A36 - طريقة التشغيل
==================================
الملفات:
  index.html         الصفحة (3 تابات + فلتر مشروع وشهر)
  chart.umd.min.js   مكتبة الرسوم (تفضل جنب الصفحة)
  data.json          البيانات (بتتولد من الإكسل)
  convert.py         بيقرأ شيتي HOM و HOM 36 ويطلّع data.json
  update.bat         دبل كليك = تحديث + رفع للموقع

تجهيز (مرة واحدة):
  1) نزّل Python من python.org (علّم Add to PATH) ثم:  pip install openpyxl pandas
  2) نزّل Git من git-scm.com
  3) اعمل حساب مجاني على github.com وأنشئ Repository جديد باسم hom-dashboard (خليه Private لو عندك خطة تدعم Pages الخاصة، وإلا Public)
  4) في فولدر الداشبورد افتح موجه الأوامر ونفّذ:
        git init
        git add .
        git commit -m "first"
        git branch -M main
        git remote add origin https://github.com/USERNAME/hom-dashboard.git
        git push -u origin main
  5) في GitHub: Settings > Pages > Source: main / root  (هيطلع لك لينك الموقع)
  6) افتح update.bat بـ Notepad وغيّر مسار الإكسل

كل مرة تحدّث:
  احفظ الإكسل ثم دبل كليك update.bat. الموقع بيتحدث خلال دقيقة.

ملحوظات مهمة:
  - GitHub Pages العامة معناها أي حد معاه اللينك يشوف الأرقام. للحماية بباسورد استخدم Cloudflare Access أو Netlify (خطة مدفوعة) - قولي وأظبطها.
  - أسماء العملاء مش بتنزل للموقع، كود الوحدة بس.
  - 3 دفعات تعاقد مسددة (حوالي 9.7 مليون، منها صفين وحدتهم "A36-" في شيت HOM) ملهاش تاريخ سداد في الإكسل، فاتحسبت بتاريخ الشيك (يناير ومايو). راجعها.
