"""공통 헬퍼 함수 (v2)"""

def fmt_krw(val):
    """원화 포맷"""
    if abs(val) >= 1e8:
        return f"₩{val/1e8:,.1f}억"
    elif abs(val) >= 1e4:
        return f"₩{val/1e4:,.0f}만"
    return f"₩{val:,.0f}"

def result_badge(r):
    """결과 뱃지 — 승/패/잉"""
    cls = {"승": "badge-win", "패": "badge-lose", "잉": "badge-ing", "진행": "badge-progress"}.get(r, "")
    return f'<span class="{cls}">{r}</span>'

def market_badge(m):
    """시장 뱃지"""
    badge_map = {
        "KOSPI": "badge-kospi",
        "KOSDAQ": "badge-kosdaq",
        "NASDAQ": "badge-nasdaq",
        "BTC": "badge-btc",
    }
    cls = badge_map.get(m, "badge-kospi")
    return f'<span class="{cls}">{m}</span>'

def fmt_date_short(dt):
    """2자리 연도 날짜 포맷 (26-03-17)"""
    try:
        return dt.strftime("%y-%m-%d")
    except Exception:
        return str(dt)

def archive_result_badge(r):
    """시그널 아카이브 결과 뱃지"""
    badge_map = {
        "Success": ("badge-win", "Success"),
        "Drop": ("badge-lose", "Drop"),
        "Continue": ("badge-ing", "Continue"),
    }
    cls, label = badge_map.get(r, ("", r))
    return f'<span class="{cls}">{label}</span>'

def tooltip_html(title, content):
    """마우스오버 툴팁 박스 (CSS hover 기반)"""
    return f"""
    <div class="tooltip-wrapper">
        <span class="tooltip-trigger">{title}</span>
        <div class="tooltip-box">{content}</div>
    </div>"""
