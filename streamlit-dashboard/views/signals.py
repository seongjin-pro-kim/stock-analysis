"""📡 시그널 — 확장 카드, 프리뷰, 톤다운 아이콘, 단일색 차트, 실패MA 패턴"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import market_badge, fmt_date_short


def render():
    signals = st.session_state.signals
    trades = st.session_state.trades

    st.markdown("### 📡 시그널 & 워치리스트")

    # ── 요약 KPI (마우스오버 프리뷰 포함) ──────────────
    total_sig = len(signals)
    strong = signals[signals["strength"] == "강"]
    medium = signals[signals["strength"] == "중"]
    weak = signals[signals["strength"] == "약"]

    completed = trades[trades["result"].isin(["승", "패"])]

    def _signal_preview(strength_label):
        """해당 강도 시그널의 최근 거래 프리뷰"""
        # 과거 매매에서 해당 등급과 비슷한 종목 찾기
        if strength_label == "강":
            sub = completed[completed.get("grade", pd.Series()) == "A"] if "grade" in completed.columns else completed.head(5)
        elif strength_label == "중":
            sub = completed[completed.get("grade", pd.Series()) == "B"] if "grade" in completed.columns else completed.head(5)
        else:
            sub = completed[completed.get("grade", pd.Series()) == "C"] if "grade" in completed.columns else completed.head(5)

        sub = sub.sort_values("date", ascending=False).head(5)
        if len(sub) == 0:
            return ""

        rows = ""
        for _, r in sub.iterrows():
            tgt_str = f"{r.get('target_rate', 0):.1f}%" if pd.notna(r.get("target_rate")) else "-"
            rows += f"""<tr style='border-bottom:1px solid #1e2530;'>
                <td style='padding:2px 4px; color:#7a8599; font-size:10px;'>{fmt_date_short(r['date'])}</td>
                <td style='padding:2px 4px; color:#e2e8f0; font-size:10px;'>{r['name']}</td>
                <td style='padding:2px 4px; color:#14b8a6; font-size:10px; text-align:right;'>{tgt_str}</td>
            </tr>"""

        return f"""<table style='width:100%; border-collapse:collapse;'>
            <thead><tr style='border-bottom:1px solid #2a3545;'>
                <th style='padding:2px 4px; color:#7a8599; font-size:9px;'>날짜</th>
                <th style='padding:2px 4px; color:#7a8599; font-size:9px;'>종목</th>
                <th style='padding:2px 4px; color:#7a8599; font-size:9px; text-align:right;'>목표율</th>
            </tr></thead><tbody>{rows}</tbody></table>"""

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, "활성 시그널", f"{total_sig}개", "neutral", ""),
        (c2, "강 시그널", f"{len(strong)}개", "positive", _signal_preview("강")),
        (c3, "중 시그널", f"{len(medium)}개", "neutral", _signal_preview("중")),
        (c4, "약 시그널", f"{len(weak)}개", "negative", _signal_preview("약")),
    ]
    for col, label, val, cls, preview in kpis:
        with col:
            if preview:
                st.markdown(f"""
                <div class="tooltip-wrapper" style="width:100%;">
                    <div class="kpi-card" style="width:100%;">
                        <div class="kpi-label">{label}</div>
                        <div class="kpi-value {cls}">{val}</div>
                    </div>
                    <div class="tooltip-box" style="bottom:auto; top:110%; left:0; transform:none;">
                        {preview}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value {cls}">{val}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 활성 시그널 카드 (확장 필드) ─────────────────────
    st.markdown("#### 활성 시그널")
    for _, s in signals.iterrows():
        strength_colors = {"강": "#22c55e", "중": "#eab308", "약": "#ef4444"}
        s_color = strength_colors.get(s["strength"], "#7a8599")

        # 거리 계산
        dist_target = ((s["target_price"] - s["current_price"]) / s["current_price"] * 100)
        dist_stop = ((s["current_price"] - s["stop_price"]) / s["current_price"] * 100)

        total_range = s["target_price"] - s["stop_price"]
        progress = (s["current_price"] - s["stop_price"]) / total_range * 100 if total_range > 0 else 50

        # 톤다운 아이콘
        vol_icon = '<span style="color:#4a5568;">▲</span>' if s["volume_spike"] else '<span style="color:#2a3545;">▽</span>'

        # 확장 필드 가져오기
        grade = s.get("grade", "-") or "-"
        tgt_rate = s.get("target_rate", 0)
        stp_rate = s.get("stop_rate", 0)
        rr = s.get("rr_ratio", 0)
        ev = s.get("expected_value", 0)

        tgt_rate_str = f"{float(tgt_rate):.1f}%" if pd.notna(tgt_rate) else "-"
        stp_rate_str = f"{float(stp_rate):.1f}%" if pd.notna(stp_rate) else "-"
        rr_str = f"{float(rr):.2f}" if pd.notna(rr) else "-"
        ev_str = f"{float(ev):.1f}" if pd.notna(ev) else "-"

        grade_colors = {"A": "#22c55e", "B": "#eab308", "C": "#ef4444"}
        g_color = grade_colors.get(grade, "#7a8599")

        st.markdown(f"""
        <div style="background:#111820; border:1px solid #1e2530; border-radius:10px; padding:16px; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="color:#e2e8f0; font-weight:600; font-size:15px;">{s['name']}</span>
                    <span style="color:#7a8599; font-size:12px;">{s['code']}</span>
                    {market_badge(s['market'])}
                    <span style="color:{g_color}; font-weight:700; font-size:12px; border:1px solid {g_color}; padding:1px 8px; border-radius:4px;">{grade}</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:{s_color}; font-weight:700; font-size:14px; border:1px solid {s_color}; padding:2px 10px; border-radius:20px;">{s['strength']}</span>
                </div>
            </div>
            <div style="display:flex; gap:16px; font-size:12px; margin-bottom:8px; flex-wrap:wrap;">
                <div><span style="color:#7a8599;">갭</span> <span style="color:#e2e8f0; font-weight:600;">{s['gap_rate']:.1f}%</span></div>
                <div><span style="color:#7a8599;">목표율</span> <span style="color:#14b8a6; font-weight:600;">{tgt_rate_str}</span></div>
                <div><span style="color:#7a8599;">목표가</span> <span style="color:#14b8a6; font-weight:600;">₩{s['target_price']:,}</span></div>
                <div><span style="color:#7a8599;">손절가</span> <span style="color:#ef4444; font-weight:600;">₩{s['stop_price']:,}</span></div>
                <div><span style="color:#7a8599;">손절율</span> <span style="color:#ef4444; font-weight:600;">{stp_rate_str}</span></div>
                <div><span style="color:#7a8599;">손익비</span> <span style="color:#e2e8f0; font-weight:600;">{rr_str}</span></div>
                <div><span style="color:#7a8599;">기대값</span> <span style="color:#e2e8f0; font-weight:600;">{ev_str}</span></div>
                <div><span style="color:#7a8599;">볼륨</span> {vol_icon}</div>
            </div>
            <div style="display:flex; gap:16px; font-size:11px; margin-bottom:8px;">
                <span style="color:#14b8a6;">목표까지 {dist_target:+.1f}%</span>
                <span style="color:#ef4444;">손절까지 -{dist_stop:.1f}%</span>
            </div>
            <div style="background:#1e2530; border-radius:4px; height:6px; overflow:hidden;">
                <div style="background:linear-gradient(90deg, #ef4444, #eab308, #22c55e); width:{min(max(progress,0),100):.0f}%; height:100%; border-radius:4px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:10px; color:#7a8599; margin-top:4px;">
                <span>손절</span><span>현재</span><span>목표</span>
            </div>
            <div style="color:#7a8599; font-size:10px; margin-top:6px;">MA: {s['ma_pattern']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 시그널 차트 (단일색 두가지 톤) ────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 시그널 갭 비율")
        fig = go.Figure(go.Bar(
            x=signals["name"],
            y=signals["gap_rate"],
            marker_color=["#14b8a6" if g >= 5 else "#0d5c54" for g in signals["gap_rate"]],
            text=[f"{v:.1f}%" for v in signals["gap_rate"]],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=11),
        ))
        fig.update_layout(
            plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(color="#7a8599"),
            yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599"),
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 볼륨 스파이크 현황")
        vol_yes = len(signals[signals["volume_spike"] == True])
        vol_no = len(signals) - vol_yes

        fig2 = go.Figure(go.Pie(
            labels=["스파이크", "일반"],
            values=[vol_yes, vol_no],
            hole=0.55,
            marker=dict(colors=["#14b8a6", "#0d3d38"]),
            textinfo="label+value",
            textfont=dict(size=12, color="#e2e8f0"),
        ))
        fig2.update_layout(
            plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False, font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MA 패턴 (성공 + 실패 나란히) ─────────────────────
    col_success, col_fail = st.columns(2)

    with col_success:
        st.markdown("#### 🏆 고승률 MA 패턴")
        ma_stats = completed.groupby("ma_pattern").agg(
            count=("result", "count"),
            wins=("result", lambda x: (x == "승").sum()),
        ).reset_index()
        ma_stats["win_rate"] = (ma_stats["wins"] / ma_stats["count"] * 100).round(1)
        ma_success = ma_stats.sort_values("win_rate", ascending=False).head(5)

        for _, m in ma_success.iterrows():
            bar_w = min(m["win_rate"], 100)
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="color:#7a8599; font-size:10px; min-width:200px;">{m['ma_pattern']}</span>
                <div style="flex:1; background:#1e2530; border-radius:4px; height:8px; overflow:hidden;">
                    <div style="background:#14b8a6; width:{bar_w}%; height:100%; border-radius:4px;"></div>
                </div>
                <span style="color:#22c55e; font-size:11px; font-weight:600; min-width:40px; text-align:right;">{m['win_rate']:.0f}%</span>
                <span style="color:#7a8599; font-size:10px;">({m['count']}건)</span>
            </div>""", unsafe_allow_html=True)

    with col_fail:
        st.markdown("#### ⚠️ 실패 MA 패턴 (하락추세)")
        # 실패 패턴: 패배 거래의 매도시점 MA 패턴
        if "sell_ma" in completed.columns:
            fail_trades = completed[completed["result"] == "패"]
            if len(fail_trades) > 0 and fail_trades["sell_ma"].notna().any():
                fail_ma = fail_trades.groupby("sell_ma").agg(
                    count=("result", "count"),
                ).reset_index()
                fail_ma = fail_ma[fail_ma["sell_ma"] != ""].sort_values("count", ascending=False).head(5)

                for _, m in fail_ma.iterrows():
                    bar_w = min(m["count"] * 20, 100)  # 스케일
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                        <span style="color:#7a8599; font-size:10px; min-width:200px;">{m['sell_ma']}</span>
                        <div style="flex:1; background:#1e2530; border-radius:4px; height:8px; overflow:hidden;">
                            <div style="background:#ef4444; width:{bar_w}%; height:100%; border-radius:4px;"></div>
                        </div>
                        <span style="color:#ef4444; font-size:11px; font-weight:600; min-width:40px; text-align:right;">{m['count']}건</span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("매도시점 MA 데이터가 부족합니다.")
        else:
            st.info("sell_ma 컬럼이 없습니다.")
