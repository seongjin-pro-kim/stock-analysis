"""공통 헬퍼 함수 (v2)"""

import streamlit as st
import pandas as pd

def fmt_krw(val):
    """원화 포맷"""
    try:
        val = float(val)
    except Exception:
        return "-"
    if abs(val) >= 1e8:
        return f"₩{val/1e8:,.1f}억"
    elif abs(val) >= 1e4:
        return f"₩{val/1e4:,.0f}만"
    return f"₩{val:,.0f}"

def result_badge(r):
    """결과 뱃지 — 승/패/잉"""
    cls = {"승": "badge-win", "패": "badge-lose", "잉": "badge-ing", "진행": "badge-progress"}.get(str(r), "")
    return f'<span class="{cls}">{r}</span>'

def market_badge(m):
    """시장 뱃지"""
    badge_map = {
        "KOSPI": "badge-kospi",
        "KOSDAQ": "badge-kosdaq",
        "NASDAQ": "badge-nasdaq",
        "BTC": "badge-btc",
    }
    cls = badge_map.get(str(m), "badge-kospi")
    return f'<span class="{cls}">{m}</span>'

def fmt_date_short(dt):
    """2자리 연도 날짜 포맷"""
    try:
        return pd.to_datetime(dt).strftime("%y-%m-%d")
    except Exception:
        return str(dt)

def archive_result_badge(r):
    """시그널 아카이브 결과 뱃지"""
    badge_map = {
        "Success": ("badge-win", "Success"),
        "Drop": ("badge-lose", "Drop"),
        "Continue": ("badge-ing", "Continue"),
    }
    cls, label = badge_map.get(str(r), ("", r))
    return f'<span class="{cls}">{label}</span>'

def tooltip_html(title, content):
    """마우스오버 툴팁 박스"""
    return f"""
    <div style="position:relative;display:inline-block;">
        <span style="border-bottom:1px dotted #999;cursor:help;">{title}</span>
        <div style="display:none;position:absolute;z-index:999;background:#111820;color:#e2e8f0;padding:10px;border:1px solid #1e2530;border-radius:8px;min-width:180px;">
            {content}
        </div>
    </div>
    """

def init_state():
    defaults = {
        "trades": [],
        "equity_curve": [],
        "positions": [],
        "signals": [],
        "signal_archive": [],
        "major_indices": [],
        "risk_metrics": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def df_state(key):
    v = st.session_state.get(key, [])
    return pd.DataFrame(v).copy() if not isinstance(v, pd.DataFrame) else v.copy()
