# ContentForge — Flask

منصة عربية لتوليد **30 فكرة فيديو** لشهر كامل: خطاف علمي + سكربت مشاهد للمصمم.

التقنية الوحيدة: **Python / Flask** (بدون Laravel أو Next.js).

## التشغيل

```powershell
cd C:\Users\Administrator\Desktop\astratgeh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

افتح: http://127.0.0.1:5000

دخول تجريبي:

- البريد: `ahmed@contentforge.ai`
- كلمة المرور: `password`

## المسار

1. نشاطك  
2. خطة 30 يوم → ولّد  
3. أفكار الفيديو / سكربت التصوير → للمصمم ثم النشر  

## هيكل المشروع

```text
app/
  routes/          # المسارات
  services/        # HookScience + StrategyGenerator
  templates/       # واجهة عربية Jinja
  static/css/      # التنسيق
run.py
requirements.txt
docs/              # ملخص أبحاث الخطاف
```
