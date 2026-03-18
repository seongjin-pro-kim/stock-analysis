"""공통 헬퍼 함수"""

def fmt_krw(val):
    """원화 포맷"""
    if abs(val) >= 1e8:
        return f"₩{val/1e8:,.1f}억"
    elif abs(val) >= 1e4:
        return f"₩{val/1e4:,.0f}만"
    return f"₩{val:,.0f}"

def result_badge(r):
    cls = {"승": "badge-win", "패": "badge-lose", "진행": "badge-progress"}.get(r, "")
    return f'<span class="{cls}">{r}</span>'

def market_badge(m):
    cls = "badge-kospi" if m == "KOSPI" else "badge-kosdaq"
    return f'<span class="{cls}">{m}</span>'
