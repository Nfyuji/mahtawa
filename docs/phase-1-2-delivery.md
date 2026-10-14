# تسليم المرحلة 1 + بداية المرحلة 2

تاريخ: 2026-10-09  
المرجع: `hh.txt`

## 1) الملفات

### توثيق
- `docs/integrations-research.md`
- `docs/architecture-phase1.md`
- `docs/phase-1-2-delivery.md`

### Backend
- جداول: `research_sources`, `integration_credentials`, `trend_queries`, `connector_runs`, `trend_observations`, `trend_snapshots`
- `App\Services\TrendDiscovery\*` (Engine, Scorer, Connectors)
- `TrendDiscoveryController`, توسيع `SettingsController`
- مسارات `/api/brands/{brand}/trends`, `/api/research-sources`, integrations

### Frontend
- `/app/trends` اكتشاف الاتجاهات
- إعدادات تكاملات YouTube / Predis
- عنصر قائمة جانبية

## 2) كيف تعمل التقنية

1. المستخدم يدخل كلمات + دولة.
2. المحرك يشغّل الموصلات المطلوبة.
3. YouTube: `videos.list?chart=mostPopular` (+ `search.list` اختياري) — رسمي.
4. Manual: JSON يرفعه المستخدم (بديل قانوني لـ Trends UI / Creative Center).
5. تُحفظ الملاحظات مع المصدر والرابط ونوع الدليل والدرجة.
6. إن نقص المفتاح → `needs_credentials` وليس بيانات وهمية.

## 3) روابط الوثائق المستخدمة
انظر `docs/integrations-research.md`.

## 4) ما يعمل / ما يحتاج اعتماد

| الميزة | الحالة |
|--------|--------|
| بحث الوثائق + المعمارية | يعمل |
| صفحة الاتجاهات + الاستيراد اليدوي | يعمل |
| موصل YouTube | يحتاج `YOUTUBE_API_KEY` أو حفظه من الإعدادات |
| PredisConnector | يحتاج API key + brand_id — إنشاء محتوى فقط |
| Google Trends API | Alpha — غير مفعّل |
| TikTok Creative Center API | غير متاح رسميًا — يدوي فقط |
| Hook Engine UI كامل | مؤجل للمرحلة 4 |

## 5) اختبار سريع

```bash
cd backend
php artisan migrate
php -S 127.0.0.1:8080 -t public

# بعد تسجيل الدخول:
# POST /api/brands/1/trends
# { "keywords": ["عطور"], "country": "SA" }
# متوقع: connector_runs يتضمن youtube_most_popular=needs_credentials بدون مفتاح
```

مع مفتاح YouTube: ملاحظات `is_fixture=false` وروابط watch.

## 6) قيود معروفة
- SQLite محليًا (PostgreSQL لاحقًا)
- لا نخلط مقاييس المنصات
- النمو غير المعروف يبقى null
- Predis Webhook endpoint لم يُبنَ بعد

## 7) تشغيل الواجهة
http://localhost:3000/app/trends  
http://localhost:3000/app/settings (تكاملات)

## 8) الخطوة التالية المقترحة
- Webhook Predis + حفظ `generated_assets`
- Hook Engine داخل Studio (5 hooks + تقييم)
- Structured Outputs لمخطط صارم
- workspaces لعزل العملاء
