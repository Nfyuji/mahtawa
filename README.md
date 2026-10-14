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
2. خطة 30 يوم → يولّد GPT ثلاثين فكرة وسيناريو مخصصًا
3. أفكار الفيديو / سكربت التصوير → للمصمم ثم النشر  

## تفعيل GPT

التوليد عبر OpenAI يعمل عند ضبط المتغيرات التالية:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1
```

يمكن حفظ المفتاح من **الإعدادات → مفتاح OpenAI**؛ يُشفّر قبل تخزينه ولا
يظهر مرة أخرى في الصفحة. ويمكن بدلًا من ذلك إضافته في Render من صفحة
**Environment**. لا تحفظ المفتاح داخل Git. حافظ على `SECRET_KEY` ثابتًا لأن
تغييره يمنع فك المفاتيح المشفرة سابقًا.

المولد يرسل بيانات البراند إلى GPT في ثلاث دفعات متوازية، ويتحقق من JSON
قبل حفظ 30 فكرة. كل فكرة تتضمن خطافات، نقاط قيمة، كلامًا منطوقًا، نصوص
الشاشة، وتعليمات التصوير.

للاستضافة الدائمة استخدم PostgreSQL واضبط `DATABASE_URL`. SQLite مناسب
للتجربة المحلية فقط؛ نظام ملفات Render المجاني قد يفقد البيانات عند إعادة النشر.

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
