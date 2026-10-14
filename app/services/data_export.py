"""Export the signed-in user's workspace data as an Excel workbook."""

from __future__ import annotations

import json
from datetime import date, datetime
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.models import Brand, User


def build_user_workbook(user: User) -> BytesIO:
    """Return an in-memory .xlsx with all brands, strategies, and content."""
    wb = Workbook()
    # Remove the default sheet; we create named ones.
    default = wb.active
    wb.remove(default)

    _sheet_account(wb, user)
    brands = (
        Brand.query.filter_by(user_id=user.id)
        .order_by(Brand.updated_at.desc())
        .all()
    )
    _sheet_brands(wb, brands)

    strategies_rows: list[list[Any]] = []
    pillars_rows: list[list[Any]] = []
    content_rows: list[list[Any]] = []
    scripts_rows: list[list[Any]] = []
    scenes_rows: list[list[Any]] = []

    for brand in brands:
        for strategy in brand.strategies or []:
            data = strategy.strategy_data or {}
            strategies_rows.append(
                [
                    brand.name,
                    strategy.id,
                    strategy.title,
                    strategy.version,
                    strategy.status,
                    _d(strategy.month_start),
                    _d(strategy.month_end),
                    strategy.primary_goal,
                    strategy.executive_summary,
                    strategy.market_summary,
                    strategy.positioning,
                    _json(data.get("objective")),
                    _json(data.get("pillars")),
                    _json(data.get("channels")),
                    _json(data.get("sprints")),
                    _json(data.get("measurement")),
                    _json(data.get("assumptions")),
                    _json(data.get("guardrails")),
                    _dt(strategy.created_at),
                ]
            )
            for pillar in strategy.pillars or []:
                pillars_rows.append(
                    [
                        brand.name,
                        strategy.id,
                        strategy.title,
                        pillar.name,
                        pillar.function,
                        pillar.distribution_percent,
                        pillar.sort_order,
                    ]
                )
            for item in strategy.items or []:
                hooks = item.hooks or []
                meta = item.virality_breakdown or {}
                content_rows.append(
                    [
                        brand.name,
                        strategy.id,
                        strategy.title,
                        item.day_number,
                        _d(item.scheduled_date),
                        item.platform,
                        item.content_type,
                        item.post_goal,
                        item.pillar_name,
                        item.title,
                        item.problem_desire,
                        item.rationale,
                        hooks[0] if hooks else "",
                        " | ".join(hooks[1:]),
                        item.cta,
                        item.creative_concept,
                        item.on_screen_text,
                        item.editing_notes,
                        item.virality_score,
                        meta.get("label") or "",
                        item.priority,
                        item.status,
                        _json(item.keywords),
                        _json(item.hashtags),
                    ]
                )
                scenes_rows.append(
                    [
                        brand.name,
                        strategy.id,
                        item.day_number,
                        item.title,
                        item.platform,
                        item.scenes or "",
                        item.script_body or "",
                    ]
                )
                script = item.script
                if script:
                    scripts_rows.append(
                        [
                            brand.name,
                            strategy.id,
                            item.day_number,
                            item.title,
                            script.hook,
                            script.promise,
                            script.problem,
                            script.body,
                            script.peak_moment,
                            script.closing,
                            script.cta,
                            " | ".join(script.alt_hooks or []),
                            " | ".join(script.alt_narratives or []),
                            script.hypothesis,
                            script.fallback_version,
                        ]
                    )

    _write_sheet(
        wb,
        "الاستراتيجيات",
        [
            "البراند",
            "رقم الاستراتيجية",
            "العنوان",
            "الإصدار",
            "الحالة",
            "بداية الشهر",
            "نهاية الشهر",
            "الهدف الأساسي",
            "الملخص التنفيذي",
            "ملخص السوق",
            "التموضع",
            "الهدف (JSON)",
            "المحاور (JSON)",
            "القنوات (JSON)",
            "الدفعات (JSON)",
            "القياس (JSON)",
            "الافتراضات (JSON)",
            "الضوابط (JSON)",
            "تاريخ الإنشاء",
        ],
        strategies_rows,
    )
    _write_sheet(
        wb,
        "المحاور",
        [
            "البراند",
            "رقم الاستراتيجية",
            "عنوان الاستراتيجية",
            "المحور",
            "الوظيفة",
            "النسبة %",
            "الترتيب",
        ],
        pillars_rows,
    )
    _write_sheet(
        wb,
        "تقويم المحتوى",
        [
            "البراند",
            "رقم الاستراتيجية",
            "عنوان الاستراتيجية",
            "اليوم",
            "التاريخ",
            "المنصة",
            "النوع",
            "الهدف",
            "المحور",
            "العنوان",
            "المشكلة/الرغبة",
            "المبرر",
            "الخطاف الأساسي",
            "خطافات بديلة",
            "الدعوة",
            "المفهوم الإبداعي",
            "نص الشاشة",
            "ملاحظات المونتاج",
            "درجة الجاهزية",
            "تسمية الجاهزية",
            "الأولوية",
            "الحالة",
            "كلمات مفتاحية",
            "هاشتاقات",
        ],
        content_rows,
    )
    _write_sheet(
        wb,
        "السيناريوهات",
        [
            "البراند",
            "رقم الاستراتيجية",
            "اليوم",
            "العنوان",
            "المنصة",
            "سيناريو التصوير الكامل",
            "نص التلقين",
        ],
        scenes_rows,
    )
    _write_sheet(
        wb,
        "النصوص المفصلة",
        [
            "البراند",
            "رقم الاستراتيجية",
            "اليوم",
            "العنوان",
            "الخطاف",
            "الوعد",
            "المشكلة",
            "النص",
            "الذروة",
            "الختام",
            "الدعوة",
            "خطافات بديلة",
            "سرديات بديلة",
            "الفرضية",
            "نسخة احتياطية",
        ],
        scripts_rows,
    )

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def export_filename(user: User) -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d")
    safe = "".join(ch for ch in (user.name or "contentforge") if ch.isalnum() or ch in "-_")
    return f"contentforge-data-{safe or 'export'}-{stamp}.xlsx"


def _sheet_account(wb: Workbook, user: User) -> None:
    rows = [
        ["الاسم", user.name],
        ["البريد", user.email],
        ["تاريخ إنشاء الحساب", _dt(user.created_at)],
        ["ملاحظة", "لا يتضمن التصدير كلمات المرور أو مفاتيح API."],
    ]
    _write_sheet(wb, "الحساب", ["الحقل", "القيمة"], rows)


def _sheet_brands(wb: Workbook, brands: list[Brand]) -> None:
    headers = [
        "الاسم",
        "الموقع",
        "الوصف",
        "المجال",
        "نموذج العمل",
        "العرض",
        "السوق",
        "اللغة",
        "اللهجة",
        "الجمهور",
        "المشكلة",
        "رغبة الجمهور",
        "مرحلة العميل",
        "الميزة التنافسية",
        "صوت العلامة",
        "المنافسون",
        "الموارد",
        "الهدف التسويقي",
        "هدف الشهر",
        "المنصات",
        "منشورات/أسبوع",
        "بداية الحملة",
        "الحالة",
        "اكتمال الملف %",
        "آخر تحديث",
    ]
    rows = []
    for brand in brands:
        rows.append(
            [
                brand.name,
                brand.website,
                brand.description,
                brand.industry,
                brand.business_model,
                brand.offer,
                brand.market,
                brand.language,
                brand.dialect,
                brand.audience,
                brand.problem,
                brand.audience_desire,
                brand.customer_stage,
                brand.competitive_advantage,
                brand.brand_voice,
                brand.competitors,
                brand.resources,
                brand.marketing_objective,
                brand.monthly_goal,
                ", ".join(brand.platforms or []),
                brand.posts_per_week,
                _d(brand.campaign_start_date),
                brand.status,
                brand.profile_completeness,
                _dt(brand.updated_at),
            ]
        )
    _write_sheet(wb, "ملف الشركة", headers, rows)


def _write_sheet(
    wb: Workbook,
    title: str,
    headers: list[str],
    rows: list[list[Any]],
) -> None:
    ws = wb.create_sheet(title[:31])
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="1F2A44")
    wrap = Alignment(wrap_text=True, vertical="top", readingOrder=2)

    ws.append(headers)
    for col_idx, _ in enumerate(headers, start=1):
        cell = ws.cell(1, col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", readingOrder=2)

    for row in rows:
        ws.append([_cell(value) for value in row])

    for row_idx in range(2, ws.max_row + 1):
        for col_idx in range(1, ws.max_column + 1):
            ws.cell(row_idx, col_idx).alignment = wrap

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    for col_idx in range(1, ws.max_column + 1):
        letter = get_column_letter(col_idx)
        max_len = len(str(headers[col_idx - 1]))
        for row_idx in range(2, min(ws.max_row, 40) + 1):
            value = ws.cell(row_idx, col_idx).value
            if value is None:
                continue
            max_len = max(max_len, min(len(str(value)), 48))
        ws.column_dimensions[letter].width = max(12, min(max_len + 2, 42))

    # Long text columns (scenes / scripts) get a taller default row feel via wrap only.
    if title in {"السيناريوهات", "النصوص المفصلة"} and ws.max_row >= 2:
        for row_idx in range(2, ws.max_row + 1):
            ws.row_dimensions[row_idx].height = 80


def _cell(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (dict, list)):
        return _json(value)
    return value


def _json(value: Any) -> str:
    if value is None or value == "" or value == [] or value == {}:
        return ""
    try:
        return json.dumps(value, ensure_ascii=False)
    except TypeError:
        return str(value)


def _d(value: date | None) -> str:
    return value.isoformat() if value else ""


def _dt(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M") if value else ""
