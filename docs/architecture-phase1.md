# Architecture — Phase 1 / 2 (ContentForge AI)

تاريخ: 2026-10-09  
مرجع المتطلبات: `hh.txt`

## القرار التقني

| الطبقة | الاختيار | السبب |
|--------|----------|--------|
| API / حسابات / صلاحيات | Laravel 12 (موجود) | لا نعيد البناء |
| واجهة | Next.js + TS RTL (موجود) | مستمر |
| DB الآن | SQLite محلي | سريع للتطوير؛ مخطط متوافق مع PostgreSQL لاحقًا |
| طوابير | Laravel Queue (database) — تفعيل تدريجي | عمليات طويلة (Predis/YouTube) |
| AI | OpenAI-compatible عبر `LlmClient` | موجود |
| تحليل ثقيل | Python/FastAPI | **لاحقًا** عند الحاجة المثبتة |
| Microservices / K8s | لا | مبكر جدًا |

## مبدأ البيانات

كل ملاحظة اتجاه يجب أن تحمل:
- `source_key` (youtube_most_popular / manual_import / …)
- `observed_at` / `fetched_at`
- رابط أو معرف أصلي عند التوفر
- `evidence_type`: `observed` | `computed` | `ai_interpretation` | `hypothesis`
- ممنوع عرض بيانات تجريبية بدون `is_fixture=true` ووسم واضح في UI

## وحدات المنتج (خريطة)

```
Trend Discovery Engine  →  Market Analyzer  →  AI Content Studio (+ Hook Engine)
         ↑                        ↓
   Connectors (YouTube, Manual, Predis*)   Content Performance Learning
```

\* Predis = إنتاج أصول، ليس مصدر ترندات.

## مخطط DB المرحلي (يُنفَّذ الآن جزئيًا)

جداول هذه المرحلة:
- `research_sources`
- `trend_queries`
- `trend_observations`
- `trend_snapshots`
- `integration_credentials` (قيم مشفّرة)
- `connector_runs` (نجاح/فشل/سبب)

جداول لاحقة (موثّقة، غير إلزامية الآن):
workspaces, subscriptions, competitor_profiles, generated_assets,
content_publications, experiments, usage_records, audit_logs

العلاقات الحالية تبقى على `brands` كعزل عميل مبسط حتى تُضاف workspaces.

## معادلة ترتيب الفرص (موثّقة وقابلة للتعديل)

```
opportunity_score =
  0.30 * relevance_to_brand   (0-100)
+ 0.25 * source_reliability   (0-100)
+ 0.20 * recency_score        (0-100)
+ 0.15 * momentum_score       (0-100 أو null → يُستبعد من المتوسط ويُعاد وزن الباقي)
+ 0.10 * evidence_strength    (0-100)
```

إذا `momentum` غير معروف → لا نختلق نموًا؛ التصنيف يصبح `needs_verification` ما لم تدعم الأدلة غير ذلك.

التصنيفات:
- `rising` — نمو محسوب من snapshots
- `steady` — حجم مستمر بلا تسارع واضح
- `seasonal` — وسم يدوي/قواعد موسمية لاحقًا
- `needs_verification` — إشارة ضعيفة
- `not_relevant` — صلة منخفضة بالعلامة

## حدود صريحة

- لا تنبؤ مؤكد بالانتشار الفيروسي
- لا مساواة بين مشاهدات YouTube واهتمام Google Trends وهاشتاقات TikTok
- لا استنتاج مبيعات المنافسين

## خطة المراحل

| مرحلة | التسليم |
|-------|---------|
| 1 | بحث وثائق + معماري + حدود تكامل ✅ |
| 2 | موصل YouTube + Manual + تقرير اتجاهات |
| 3 | ترتيب/تصنيف + تلخيص بأدلة |
| 4 | Content Studio + Predis عند المفتاح |
| 5 | أداء منشورات + عزل/أمان متقدم |
