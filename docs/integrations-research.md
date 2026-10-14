# Integrations Research — ContentForge AI

تاريخ المراجعة: 2026-10-09  
القاعدة: وثائق رسمية فقط. لا Scraping مخالف. لا اختراع endpoints.

## حالة المشروع الحالي (قبل هذه المرحلة)

موجود فعليًا:
- Laravel 12 API + Sanctum + SQLite
- Next.js RTL dashboard
- Growth Engine (Master Prompt / Strategy / Studio / Learning)
- Social Listening pipeline داخلي (corpus منظم + AI اختياري) — **ليس** اتصال firehose رسمي
- إعدادات OpenAI من الواجهة (مفتاح مشفّر)

غير موجود بعد (مطلوب حسب `hh.txt`):
- Trend Discovery Engine بموصلات رسمية منفصلة
- PredisConnector
- عزل workspaces متعدد العملاء بشكل كامل
- post analytics من APIs المنصات
- Hook Engine UI متقدم

---

## 1) Predis.ai API

| البند | التفاصيل |
|--------|-----------|
| الحالة | **يحتاج بيانات اعتماد** |
| الوثائق | [Quick Start](https://predis.ai/developers/docs/predis-api/quick-start/) · [Create Content](https://predis.ai/developers/docs/predis-api/API%20reference/create-content-api/) |
| الوظائف المتاحة رسميًا | إنشاء محتوى (صورة/كاروسيل/فيديو حسب `media_type` و`model_version`)، استلام حالة عبر Webhook، ربط Brand ID |
| Endpoint موثق | `POST https://brain.predis.ai/predis_api/v1/create_content/` (form-data) |
| المصادقة | Header `Authorization: YOUR_API_KEY` |
| بيانات مطلوبة | `brand_id`, `text` (≥ 3 كلمات و20 حرفًا)، اختياري: `media_type`, `model_version`, `n_posts`, لغات، إلخ |
| الاستجابة | `post_ids`, `post_status` (`inProgress`)، `errors` — النتيجة النهائية عبر Webhook |
| القيود الموثقة | 429 rate limit؛ حد credits؛ حد 3 posts `inProgress`؛ قيود توافق `model_version`/`media_type` |
| ما لا يتوفر في هذه الوثائق | اكتشاف ترندات المنصات، نشر مباشر لكل الشبكات كبديل عن Trend Engine |
| الإعداد | مفتاح من Pricing & Account → Rest API؛ Webhook URL؛ Brand ID |
| الاختبار | بدون مفتاح: موصل + tests ببيانات تجريبية موسومة فقط |

**ملاحظة:** Predis = إنتاج محتوى مرئي، منفصل عن اكتشاف الاتجاهات.

---

## 2) OpenAI Text + Structured Outputs

| البند | التفاصيل |
|--------|-----------|
| الحالة | **متحقق جزئيًا** (مستخدم عبر `LlmClient` + إعدادات المستخدم) |
| الوثائق | [Text generation](https://developers.openai.com/api/docs/guides/text) · [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) |
| الوظائف | تلخيص، تصنيف، توليد نصوص/سيناريوهات، JSON منظم |
| المصادقة | Bearer API key |
| الاستخدام الصحيح | تمرير أدلة مجمعة للنموذج — **ممنوع** طلب اختلاق ترندات/إحصاءات |
| القيود | تكلفة حسب الاستخدام؛ حدود rate؛ لا وصول تلقائي لحسابات السوشيال |
| ما لا يفعله | ليس مصدر بيانات ترندات؛ ليس بديل YouTube/Meta APIs |

تحسين مطلوب لاحقًا: الانتقال من `response_format: json_object` إلى Structured Outputs بمخطط صارم.

---

## 3) Google Trends

| البند | التفاصيل |
|--------|-----------|
| الحالة | **يحتاج اعتماد Alpha** |
| الوثائق | [Trends API Alpha](https://developers.google.com/search/apis/trends) · [إعلان 2025-07](https://developers.google.com/search/blog/2025/07/trends-api) |
| الوظائف المعلنة | اهتمام بحث نسبي متسق القياس؛ نافذة ~1800 يوم؛ تجميع يومي/أسبوعي/شهري/سنوي؛ مناطق |
| المصادقة | OAuth / موافقة Alpha (الوصول محدود للمختبرين) |
| ما لا يمكن الآن بدون موافقة | استدعاء إنتاجي عام من كل حساب |
| البديل القانوني الحالي | إدخال يدوي لقطات من trends.google.com، أو رفع CSV، مع وسم المصدر `manual_google_trends` |
| ممنوع | مكتبات scraping غير رسمية كمصدر «رسمي» |

Help UI: [Google Trends Help](https://support.google.com/trends/)

---

## 4) TikTok Creative Center / Trends

| البند | التفاصيل |
|--------|-----------|
| الحالة | **غير متاح كـ API رسمي عام للاستخدام البرمجي** (حسب مراجعة 2026-10-09) |
| الواجهة البشرية | [Creative Center](https://ads.tiktok.com/business/creativecenter/) · [How to use trends](https://ads.tiktok.com/resources/help/article/how-to-use-trends) |
| مطورو TikTok الرسميون | [developers.tiktok.com](https://developers.tiktok.com/) — Login Kit، Content Posting، Data Portability (EEA/UK)… **لا** وثيقة رسمية لـ Creative Center Trends API في هذه المراجعة |
| ما لا نفعله | استخدام APIs طرف ثالث غير رسمية أو scraping كأنها مصدر TikTok الرسمي |
| البديل القانوني | رفع ملف/لقطة يدوية من Creative Center؛ أو ربط Content Posting لاحقًا للنشر بعد موافقة المستخدم |

---

## 5) YouTube Data API v3

| البند | التفاصيل |
|--------|-----------|
| الحالة | **موصل رسمي قابل للتنفيذ** (يحتاج `YOUTUBE_API_KEY`) |
| الوثائق | [videos.list](https://developers.google.com/youtube/v3/docs/videos/list) · [mostPopular guide](https://developers.google.com/youtube/v3/guides/implementation/videos) · [search.list](https://developers.google.com/youtube/v3/docs/search/list) |
| للاتجاهات | `videos.list?chart=mostPopular&regionCode=SA&part=snippet,statistics` |
| للبحث | `search.list?q=...&type=video&order=viewCount|date|relevance` |
| المصادقة | API Key للبيانات العامة؛ OAuth لبيانات الحساب الخاص |
| البيانات | عناوين، أوصاف، إحصاءات عامة (مشاهدات/إعجابات عند توفرها)، معرفات فيديو، روابط |
| القيود | حصص يومية (quota units)؛ ليس «Google Trends»؛ `mostPopular` ≠ ضمان نجاح محتواك |
| ما لا يستنتج | مبيعات/تحويلات المنافسين |

---

## 6) Meta (Facebook/Instagram) Graph API

| البند | التفاصيل |
|--------|-----------|
| الحالة | **يحتاج بيانات اعتماد + مراجعة صلاحيات App** |
| الوثائق | [Meta for Developers](https://developers.facebook.com/docs/) (Graph API / Instagram APIs) |
| الاستخدام المحتمل لاحقًا | رؤى حساب العميل بعد OAuth؛ ليس بديلاً عن Creative Center |
| قيود | صلاحيات حساسة، مراجعة Meta، لا تفترض توفر Insights لكل حالة |
| المرحلة الحالية | توثيق فقط — لا تكامل قبل إعداد App ومراجعته |

---

## 7) مصادر عامة موثوقة / يدوية

| المصدر | الحالة | الاستخدام |
|--------|--------|-----------|
| رفع CSV/JSON يدوي | **متاح** | لقطات Google Trends / Creative Center / تقارير داخلية |
| رابط مصدر + ملاحظة | **متاح** | دليل بشري مع `reliability_score` منخفض إن لم يُتحقق آليًا |
| أخبار عامة عبر API رسمي | لاحقًا | فقط إن وُثّق موصل بعينه |

---

## ملخص حالات التكامل

| المصدر | الحالة |
|--------|--------|
| OpenAI | متحقق جزئيًا — تحسين Structured Outputs لاحقًا |
| YouTube Data API | جاهز للتنفيذ — يحتاج مفتاح |
| Predis.ai Create Content | موصل جاهز للهيكل — يحتاج مفتاح + Brand ID + Webhook |
| Google Trends API | Alpha — يحتاج موافقة؛ بديل يدوي الآن |
| TikTok Creative Center | لا API رسمي عام — بديل يدوي فقط |
| Meta Graph | مؤجل حتى بيانات الاعتماد |

---

## الخطوة التالية بعد هذا الملف

1. مخطط معماري وقاعدة بيانات مرحلي (`docs/architecture-phase1.md`)
2. تنفيذ `TrendDiscoveryEngine` + موصل YouTube الرسمي + الاستيراد اليدوي
3. صفحة UI لاكتشاف الاتجاهات مع أدلة ومصادر — بدون بيانات وهمية تُعرض كحقيقية
