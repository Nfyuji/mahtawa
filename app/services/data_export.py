"""Export the signed-in user's workspace as a polished Excel workbook."""

from __future__ import annotations

import json
from datetime import date, datetime
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from app.models import Brand, User

# ---------------------------------------------------------------------------
#  Design tokens
# ---------------------------------------------------------------------------

NAVY = "0F1B33"
NAVY_SOFT = "1B2B4A"
TEAL = "0D9488"
TEAL_SOFT = "CCFBF1"
AMBER = "B45309"
AMBER_SOFT = "FEF3C7"
VIOLET = "6D28D9"
VIOLET_SOFT = "EDE9FE"
ROSE = "BE123C"
ROSE_SOFT = "FFE4E6"
SLATE = "64748B"
SLATE_SOFT = "F1F5F9"
WHITE = "FFFFFF"
INK = "0F172A"
MUTED = "475569"
ROW_A = "FFFFFF"
ROW_B = "F8FAFC"
GREEN = "15803D"
GREEN_SOFT = "DCFCE7"
BLUE = "1D4ED8"
BLUE_SOFT = "DBEAFE"

SHEET_COLORS = {
    "دليل الملف": TEAL,
    "الحساب": SLATE,
    "ملف الشركة": VIOLET,
    "الاستراتيجيات": TEAL,
    "المحاور": AMBER,
    "تقويم المحتوى": BLUE,
    "السيناريوهات": ROSE,
    "النصوص المفصلة": NAVY_SOFT,
}

PLATFORM_AR = {
    "tiktok": "تيك توك",
    "instagram": "إنستغرام",
    "youtube": "يوتيوب",
    "x": "X",
    "facebook": "فيسبوك",
}
GOAL_AR = {
    "discovery": "وصول واكتشاف",
    "trust": "ثقة",
    "engagement": "تفاعل",
    "conversion": "تحويل",
}
TYPE_AR = {
    "short_video": "فيديو قصير",
    "carousel": "كاروسيل",
    "text_post": "منشور نصي",
    "story": "قصة",
}


def build_user_workbook(user: User) -> BytesIO:
    """Return an in-memory .xlsx with branded formatting."""
    wb = Workbook()
    wb.remove(wb.active)

    brands = (
        Brand.query.filter_by(user_id=user.id)
        .order_by(Brand.updated_at.desc())
        .all()
    )

    strategies_rows: list[list[Any]] = []
    pillars_rows: list[list[Any]] = []
    content_rows: list[list[Any]] = []
    scenes_rows: list[list[Any]] = []
    scripts_rows: list[list[Any]] = []
    strategy_count = 0
    item_count = 0

    for brand in brands:
        for strategy in brand.strategies or []:
            strategy_count += 1
            data = strategy.strategy_data or {}
            objective = data.get("objective") or {}
            strategies_rows.append(
                [
                    brand.name,
                    strategy.version,
                    strategy.title,
                    strategy.status,
                    _d(strategy.month_start),
                    _d(strategy.month_end),
                    strategy.primary_goal or objective.get("goal_text") or "",
                    objective.get("primary_kpi") or "",
                    strategy.executive_summary or "",
                    strategy.positioning or "",
                    " · ".join(data.get("assumptions") or [])[:500],
                    _dt(strategy.created_at),
                ]
            )
            for pillar in strategy.pillars or []:
                pillars_rows.append(
                    [
                        brand.name,
                        f"v{strategy.version}",
                        pillar.sort_order,
                        pillar.name,
                        pillar.function or "",
                        pillar.distribution_percent or 0,
                    ]
                )
            for item in strategy.items or []:
                item_count += 1
                hooks = item.hooks or []
                meta = item.virality_breakdown or {}
                content_rows.append(
                    [
                        brand.name,
                        f"v{strategy.version}",
                        item.day_number or "",
                        _d(item.scheduled_date),
                        PLATFORM_AR.get(item.platform, item.platform or ""),
                        TYPE_AR.get(item.content_type, item.content_type or ""),
                        GOAL_AR.get(item.post_goal, item.post_goal or ""),
                        item.pillar_name or "",
                        item.title or "",
                        item.problem_desire or "",
                        hooks[0] if hooks else "",
                        " | ".join(hooks[1:4]),
                        item.cta or "",
                        item.virality_score or 0,
                        meta.get("label") or "",
                        item.priority or "",
                        item.status or "",
                    ]
                )
                scenes_rows.append(
                    [
                        brand.name,
                        item.day_number or "",
                        item.title or "",
                        PLATFORM_AR.get(item.platform, item.platform or ""),
                        item.scenes or "",
                        item.script_body or "",
                    ]
                )
                script = item.script
                if script:
                    scripts_rows.append(
                        [
                            brand.name,
                            item.day_number or "",
                            item.title or "",
                            script.hook or "",
                            script.promise or "",
                            script.problem or "",
                            script.body or "",
                            script.peak_moment or "",
                            script.closing or "",
                            script.cta or "",
                            " | ".join(script.alt_hooks or []),
                            script.hypothesis or "",
                        ]
                    )

    _sheet_guide(wb, user, len(brands), strategy_count, item_count)
    _sheet_account(wb, user, len(brands), strategy_count, item_count)
    _sheet_brands(wb, brands)
    _write_sheet(
        wb,
        "الاستراتيجيات",
        "كل إصدارات الاستراتيجية بملخص واضح",
        TEAL,
        [
            "البراند",
            "الإصدار",
            "العنوان",
            "الحالة",
            "بداية الشهر",
            "نهاية الشهر",
            "الهدف",
            "KPI",
            "الملخص التنفيذي",
            "التموضع",
            "افتراضات للمراجعة",
            "تاريخ الإنشاء",
        ],
        strategies_rows,
        widths={1: 18, 2: 10, 3: 34, 4: 12, 7: 28, 8: 18, 9: 40, 10: 28, 11: 36},
        accent_cols={4: "status"},
    )
    _write_sheet(
        wb,
        "المحاور",
        "توزيع محاور المحتوى ونسبها",
        AMBER,
        ["البراند", "الإصدار", "الترتيب", "المحور", "الوظيفة", "النسبة %"],
        pillars_rows,
        widths={1: 18, 2: 10, 3: 10, 4: 28, 5: 24, 6: 12},
        accent_cols={6: "percent"},
    )
    _write_sheet(
        wb,
        "تقويم المحتوى",
        "30 يومًا — عنوان، خطاف، منصة، وجاهزية الاختبار",
        BLUE,
        [
            "البراند",
            "الإصدار",
            "اليوم",
            "التاريخ",
            "المنصة",
            "النوع",
            "الهدف",
            "المحور",
            "العنوان",
            "المشكلة",
            "الخطاف الأساسي",
            "خطافات بديلة",
            "الدعوة",
            "الجاهزية",
            "التسمية",
            "الأولوية",
            "الحالة",
        ],
        content_rows,
        widths={
            1: 16,
            3: 8,
            4: 12,
            5: 12,
            6: 12,
            7: 14,
            8: 16,
            9: 32,
            10: 28,
            11: 30,
            12: 26,
            13: 22,
            14: 10,
            15: 18,
        },
        accent_cols={5: "platform", 14: "score", 16: "priority"},
        score_col=14,
        tall=False,
    )
    _write_sheet(
        wb,
        "السيناريوهات",
        "سيناريو التصوير الكامل + التلقين المتصل",
        ROSE,
        [
            "البراند",
            "اليوم",
            "العنوان",
            "المنصة",
            "سيناريو التصوير الكامل",
            "نص التلقين",
        ],
        scenes_rows,
        widths={1: 16, 2: 8, 3: 28, 4: 12, 5: 55, 6: 45},
        accent_cols={4: "platform"},
        tall=True,
    )
    _write_sheet(
        wb,
        "النصوص المفصلة",
        "خطاف · وعد · مشكلة · نص · دعوة",
        NAVY_SOFT,
        [
            "البراند",
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
            "الفرضية",
        ],
        scripts_rows,
        widths={1: 14, 2: 8, 3: 26, 4: 28, 5: 24, 6: 24, 7: 40, 10: 22, 12: 28},
        tall=True,
    )

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def export_filename(user: User) -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M")
    safe = "".join(ch for ch in (user.name or "contentforge") if ch.isalnum() or ch in "-_")
    # V3 in the name so the user can tell they got the colored redesign.
    return f"ContentForge-Export-V3-{safe or 'export'}-{stamp}.xlsx"


# ---------------------------------------------------------------------------
#  Sheets
# ---------------------------------------------------------------------------


def _sheet_guide(wb: Workbook, user: User, brands: int, strategies: int, items: int) -> None:
    ws = wb.create_sheet("دليل الملف", 0)
    ws.sheet_view.rightToLeft = True
    ws.sheet_properties.tabColor = TEAL

    _banner(ws, "ContentForge Export V3 — تنسيق ملوّن جديد", 6, TEAL)
    ws.merge_cells("A2:F2")
    ws["A2"] = (
        f"مرحباً {user.name} · نسخة التنسيق V3 · تم التصدير {_dt(datetime.utcnow())} "
        "· إذا لم ترَ ورقة «دليل الملف» فأنت تفتح ملفًا قديمًا"
    )
    ws["A2"].font = Font(name="Calibri", size=12, color=NAVY, bold=True)
    ws["A2"].fill = PatternFill("solid", fgColor=AMBER_SOFT)
    ws["A2"].alignment = Alignment(horizontal="right", vertical="center", readingOrder=2)
    ws.row_dimensions[2].height = 26

    # Summary cards row
    cards = [
        ("A4", "البراندات", str(brands), VIOLET, VIOLET_SOFT),
        ("C4", "الاستراتيجيات", str(strategies), TEAL, TEAL_SOFT),
        ("E4", "قطع المحتوى", str(items), BLUE, BLUE_SOFT),
    ]
    for start, label, value, fg, bg in cards:
        col = start[0]
        next_col = chr(ord(col) + 1)
        ws.merge_cells(f"{start}:{next_col}4")
        ws.merge_cells(f"{col}5:{next_col}5")
        top = ws[start]
        top.value = label
        top.font = Font(name="Calibri", size=11, color=fg, bold=True)
        top.fill = PatternFill("solid", fgColor=bg)
        top.alignment = Alignment(horizontal="center", vertical="center")
        bottom = ws[f"{col}5"]
        bottom.value = value
        bottom.font = Font(name="Calibri", size=28, color=fg, bold=True)
        bottom.fill = PatternFill("solid", fgColor=bg)
        bottom.alignment = Alignment(horizontal="center", vertical="center")
        ws[f"{next_col}4"].fill = PatternFill("solid", fgColor=bg)
        ws[f"{next_col}5"].fill = PatternFill("solid", fgColor=bg)

    ws.row_dimensions[4].height = 22
    ws.row_dimensions[5].height = 42

    ws["A7"] = "محتويات الملف"
    ws["A7"].font = Font(name="Calibri", size=14, bold=True, color=NAVY)
    headers = ["الورقة", "ماذا فيها؟", "اللون"]
    for idx, h in enumerate(headers, start=1):
        cell = ws.cell(8, idx, h)
        cell.font = Font(name="Calibri", bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    guide_rows = [
        ("الحساب", "اسمك وبريدك وتاريخ الحساب", SLATE),
        ("ملف الشركة", "كل حقول البراند والجمهور والهدف", VIOLET),
        ("الاستراتيجيات", "ملخص كل إصدار: هدف، KPI، تموضع", TEAL),
        ("المحاور", "أسماء المحاور ونسب التوزيع", AMBER),
        ("تقويم المحتوى", "اليوم · المنصة · العنوان · الخطاف · الجاهزية", BLUE),
        ("السيناريوهات", "سكربت التصوير الكامل جاهز للقراءة", ROSE),
        ("النصوص المفصلة", "تلقين مفصّل: خطاف ووعد ومشكلة ودعوة", NAVY_SOFT),
    ]
    for r_idx, (name, desc, color) in enumerate(guide_rows, start=9):
        ws.cell(r_idx, 1, name).font = Font(name="Calibri", bold=True, color=INK)
        ws.cell(r_idx, 2, desc).font = Font(name="Calibri", color=MUTED)
        chip = ws.cell(r_idx, 3, "■■■")
        chip.font = Font(name="Calibri", color=color, bold=True)
        chip.alignment = Alignment(horizontal="center")
        fill = PatternFill("solid", fgColor=ROW_B if r_idx % 2 == 0 else ROW_A)
        for c in range(1, 4):
            ws.cell(r_idx, c).fill = fill
            ws.cell(r_idx, c).border = _thin_border()
            ws.cell(r_idx, c).alignment = Alignment(
                horizontal="right", vertical="center", readingOrder=2, wrap_text=True
            )

    ws["A17"] = "كيف تستخدمه؟"
    ws["A17"].font = Font(name="Calibri", size=14, bold=True, color=NAVY)
    tips = [
        "1) ابدأ بورقة «تقويم المحتوى» لترى الخطة كاملة.",
        "2) افتح «السيناريوهات» وانسخ عمود سيناريو التصوير مباشرة للكاميرا.",
        "3) استخدم الفلاتر في الصف العلوي لتصفية منصة أو يوم.",
        "4) درجة الجاهزية ملوّنة: أخضر = جاهز للاختبار · أصفر = يحتاج مراجعة.",
        "5) الملف لا يحتوي كلمة المرور ولا مفتاح OpenAI.",
    ]
    for idx, tip in enumerate(tips, start=18):
        ws.merge_cells(f"A{idx}:F{idx}")
        cell = ws[f"A{idx}"]
        cell.value = tip
        cell.font = Font(name="Calibri", size=11, color=INK)
        cell.fill = PatternFill("solid", fgColor=TEAL_SOFT if idx % 2 == 0 else WHITE)
        cell.alignment = Alignment(horizontal="right", readingOrder=2, vertical="center")
        ws.row_dimensions[idx].height = 22

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 52
    ws.column_dimensions["C"].width = 12
    for col in ("D", "E", "F"):
        ws.column_dimensions[col].width = 14
    ws.row_dimensions[1].height = 36
    ws.print_title_rows = "1:1"


def _sheet_account(
    wb: Workbook, user: User, brands: int, strategies: int, items: int
) -> None:
    rows = [
        ["الاسم", user.name],
        ["البريد", user.email],
        ["تاريخ إنشاء الحساب", _dt(user.created_at)],
        ["عدد البراندات", brands],
        ["عدد الاستراتيجيات", strategies],
        ["عدد قطع المحتوى", items],
        ["خصوصية التصدير", "لا يتضمن كلمات المرور أو مفاتيح API"],
    ]
    _write_kv_sheet(wb, "الحساب", "بيانات الحساب — بدون أسرار", SLATE, rows)


def _sheet_brands(wb: Workbook, brands: list[Brand]) -> None:
    headers = [
        "الاسم",
        "الموقع",
        "الوصف",
        "المجال",
        "العرض",
        "السوق",
        "اللهجة",
        "الجمهور",
        "المشكلة",
        "رغبة الجمهور",
        "الميزة التنافسية",
        "صوت العلامة",
        "الهدف التسويقي",
        "هدف الشهر",
        "المنصات",
        "منشورات/أسبوع",
        "بداية الحملة",
        "اكتمال الملف %",
        "آخر تحديث",
    ]
    rows = []
    for brand in brands:
        rows.append(
            [
                brand.name,
                brand.website or "",
                brand.description or "",
                brand.industry or "",
                brand.offer or "",
                brand.market or "",
                brand.dialect or "",
                brand.audience or "",
                brand.problem or "",
                brand.audience_desire or "",
                brand.competitive_advantage or "",
                brand.brand_voice or "",
                brand.marketing_objective or "",
                brand.monthly_goal or "",
                ", ".join(brand.platforms or []),
                brand.posts_per_week or "",
                _d(brand.campaign_start_date),
                brand.profile_completeness,
                _dt(brand.updated_at),
            ]
        )
    _write_sheet(
        wb,
        "ملف الشركة",
        "هوية البراند والجمهور والهدف",
        VIOLET,
        headers,
        rows,
        widths={
            1: 18,
            2: 22,
            3: 32,
            4: 14,
            5: 28,
            8: 28,
            9: 28,
            10: 22,
            11: 24,
            14: 24,
            15: 20,
            18: 12,
        },
        accent_cols={18: "percent"},
    )


# ---------------------------------------------------------------------------
#  Sheet writers
# ---------------------------------------------------------------------------


def _write_kv_sheet(
    wb: Workbook,
    title: str,
    subtitle: str,
    accent: str,
    rows: list[list[Any]],
) -> None:
    ws = wb.create_sheet(title[:31])
    ws.sheet_view.rightToLeft = True
    ws.sheet_properties.tabColor = accent
    _banner(ws, f"{title} — {subtitle}", 2, accent)

    label_fill = PatternFill("solid", fgColor=SLATE_SOFT)
    label_font = Font(name="Calibri", bold=True, color=NAVY, size=11)
    value_font = Font(name="Calibri", color=INK, size=11)

    for r_idx, (label, value) in enumerate(rows, start=2):
        label_cell = ws.cell(r_idx, 1, label)
        value_cell = ws.cell(r_idx, 2, _cell(value))
        label_cell.font = label_font
        label_cell.fill = label_fill
        label_cell.alignment = Alignment(horizontal="right", vertical="center", readingOrder=2)
        value_cell.font = value_font
        value_cell.alignment = Alignment(
            horizontal="right", vertical="center", readingOrder=2, wrap_text=True
        )
        for c in (1, 2):
            ws.cell(r_idx, c).border = _thin_border()
        if r_idx % 2 == 0:
            value_cell.fill = PatternFill("solid", fgColor=ROW_B)
        ws.row_dimensions[r_idx].height = 24

    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 55
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 32


def _write_sheet(
    wb: Workbook,
    title: str,
    subtitle: str,
    accent: str,
    headers: list[str],
    rows: list[list[Any]],
    *,
    widths: dict[int, int] | None = None,
    accent_cols: dict[int, str] | None = None,
    score_col: int | None = None,
    tall: bool = False,
) -> None:
    ws = wb.create_sheet(title[:31])
    ws.sheet_view.rightToLeft = True
    ws.sheet_properties.tabColor = accent

    col_count = len(headers)
    _banner(ws, f"{title} — {subtitle}", col_count, accent)

    # Empty-state friendly note
    if not rows:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=col_count)
        empty = ws.cell(2, 1, "لا توجد بيانات في هذه الورقة بعد — أنشئ استراتيجية ثم صدّر مرة أخرى.")
        empty.font = Font(name="Calibri", italic=True, color=MUTED, size=11)
        empty.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 28

    header_fill = PatternFill("solid", fgColor=accent)
    header_font = Font(name="Calibri", bold=True, color=WHITE, size=12)
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(2, col_idx, header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(
            left=Side(style="thin", color=WHITE),
            right=Side(style="thin", color=WHITE),
            top=Side(style="thin", color=WHITE),
            bottom=Side(style="medium", color=NAVY),
        )
    ws.row_dimensions[2].height = 32

    body_font = Font(name="Calibri", size=10, color=INK)
    day_col = next((i for i, h in enumerate(headers, start=1) if h == "اليوم"), None)
    brand_col = next((i for i, h in enumerate(headers, start=1) if h == "البراند"), None)
    for r_offset, row in enumerate(rows):
        r_idx = r_offset + 3
        # Stronger zebra so color is obvious even in Google Sheets.
        zebra = PatternFill(
            "solid",
            fgColor="E0F2FE" if r_offset % 2 else ROW_A,
        )
        for c_idx, value in enumerate(row, start=1):
            cell = ws.cell(r_idx, c_idx, _cell(value))
            cell.font = body_font
            cell.fill = zebra
            cell.border = _thin_border()
            cell.alignment = Alignment(
                wrap_text=True,
                vertical="top",
                horizontal="right",
                readingOrder=2,
            )
            if brand_col and c_idx == brand_col:
                cell.fill = PatternFill("solid", fgColor=VIOLET_SOFT)
                cell.font = Font(name="Calibri", size=10, bold=True, color=VIOLET)
            if day_col and c_idx == day_col and value not in ("", None):
                cell.fill = PatternFill("solid", fgColor=TEAL_SOFT)
                cell.font = Font(name="Calibri", size=12, bold=True, color=TEAL)
                cell.alignment = Alignment(horizontal="center", vertical="center")
            _apply_accent(cell, value, (accent_cols or {}).get(c_idx))

        if tall:
            ws.row_dimensions[r_idx].height = 90
        else:
            ws.row_dimensions[r_idx].height = 38 if col_count > 10 else 26

    # Freeze banner + header
    ws.freeze_panes = "A3"
    if rows:
        last_col = get_column_letter(col_count)
        ws.auto_filter.ref = f"A2:{last_col}{2 + len(rows)}"

    # Column widths
    for col_idx in range(1, col_count + 1):
        letter = get_column_letter(col_idx)
        if widths and col_idx in widths:
            ws.column_dimensions[letter].width = widths[col_idx]
        else:
            sample = len(headers[col_idx - 1])
            for row in rows[:25]:
                if col_idx - 1 < len(row) and row[col_idx - 1] is not None:
                    sample = max(sample, min(len(str(row[col_idx - 1])), 40))
            ws.column_dimensions[letter].width = max(10, min(sample + 2, 36))

    if score_col and rows:
        letter = get_column_letter(score_col)
        ws.conditional_formatting.add(
            f"{letter}3:{letter}{2 + len(rows)}",
            ColorScaleRule(
                start_type="num",
                start_value=0,
                start_color="FECACA",
                mid_type="num",
                mid_value=70,
                mid_color="FEF08A",
                end_type="num",
                end_value=100,
                end_color="86EFAC",
            ),
        )

    ws.print_title_rows = "1:2"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0


def _banner(ws: Worksheet, text: str, col_count: int, accent: str) -> None:
    cols = max(col_count, 1)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=cols)
    cell = ws.cell(1, 1, f"★ {text}")
    cell.font = Font(name="Calibri", size=16, bold=True, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=accent)
    cell.alignment = Alignment(horizontal="right", vertical="center", readingOrder=2)
    for col in range(1, cols + 1):
        ws.cell(1, col).fill = PatternFill("solid", fgColor=accent)
        ws.cell(1, col).border = Border(
            bottom=Side(style="medium", color=NAVY)
        )
    ws.row_dimensions[1].height = 40


def _apply_accent(cell, value: Any, kind: str | None) -> None:
    if not kind:
        return
    text = str(value or "").strip().lower()
    if kind == "platform":
        mapping = {
            "تيك توك": (TEAL, TEAL_SOFT),
            "إنستغرام": (ROSE, ROSE_SOFT),
            "يوتيوب": (ROSE, "FEE2E2"),
            "x": (INK, SLATE_SOFT),
            "فيسبوك": (BLUE, BLUE_SOFT),
        }
        colors = mapping.get(str(value).strip()) or mapping.get(text)
        if colors:
            cell.font = Font(name="Calibri", size=10, bold=True, color=colors[0])
            cell.fill = PatternFill("solid", fgColor=colors[1])
            cell.alignment = Alignment(horizontal="center", vertical="center")
    elif kind == "status":
        if text in {"ready", "جاهز", "active"}:
            cell.font = Font(name="Calibri", size=10, bold=True, color=GREEN)
            cell.fill = PatternFill("solid", fgColor=GREEN_SOFT)
        else:
            cell.font = Font(name="Calibri", size=10, bold=True, color=AMBER)
            cell.fill = PatternFill("solid", fgColor=AMBER_SOFT)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    elif kind == "priority":
        mapping = {
            "high": (ROSE, ROSE_SOFT),
            "مرتفع": (ROSE, ROSE_SOFT),
            "medium": (AMBER, AMBER_SOFT),
            "متوسط": (AMBER, AMBER_SOFT),
            "low": (SLATE, SLATE_SOFT),
            "منخفض": (SLATE, SLATE_SOFT),
        }
        colors = mapping.get(text)
        if colors:
            cell.font = Font(name="Calibri", size=10, bold=True, color=colors[0])
            cell.fill = PatternFill("solid", fgColor=colors[1])
            cell.alignment = Alignment(horizontal="center", vertical="center")
    elif kind == "percent":
        try:
            num = float(value)
        except (TypeError, ValueError):
            return
        if num >= 70:
            cell.font = Font(name="Calibri", size=10, bold=True, color=GREEN)
            cell.fill = PatternFill("solid", fgColor=GREEN_SOFT)
        elif num >= 40:
            cell.font = Font(name="Calibri", size=10, bold=True, color=AMBER)
            cell.fill = PatternFill("solid", fgColor=AMBER_SOFT)
        else:
            cell.font = Font(name="Calibri", size=10, bold=True, color=ROSE)
            cell.fill = PatternFill("solid", fgColor=ROSE_SOFT)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    elif kind == "score":
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(name="Calibri", size=11, bold=True, color=INK)


def _thin_border() -> Border:
    side = Side(style="thin", color="E2E8F0")
    return Border(left=side, right=side, top=side, bottom=side)


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
