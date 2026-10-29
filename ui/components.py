"""Reusable Professional UI Components for MediRoute Emergency Dashboard."""

from __future__ import annotations
from typing import Any, Optional
import streamlit as st
from ui.auth import get_current_user, logout_user


def render_command_bar(
    title: str = "Overview Dashboard",
    subtitle: str = "Emergency Fleet & Dispatch Operations",
    show_dispatch_btn: bool = True,
    show_reset_btn: bool = True,
    simulation_step: int = 1,
    **kwargs: Any,
) -> None:
    """Render the top command-and-control bar with authentication status."""
    current_user = get_current_user()

    col_brand, col_actions = st.columns([5, 7])

    with col_brand:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.05rem 0;">
                <div style="display: flex; align-items: center; justify-content: center; width: 34px; height: 34px; background: #0F9D92; color: #FFFFFF; border-radius: 8px; font-weight: 800; font-size: 1.15rem; box-shadow: 0 2px 4px rgba(15, 157, 146, 0.25);">
                    ✚
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.25rem; font-weight: 700; color: #0F172A; letter-spacing: -0.02em;">
                            MediRoute
                        </span>
                        <span style="color: #CBD5E1; font-weight: 300;">/</span>
                        <span style="font-size: 1.15rem; font-weight: 600; color: #1E293B;">
                            {title}
                        </span>
                    </div>
                    <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.05rem;">
                        {subtitle}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_actions:
        st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)
        act_c1, act_c2, act_c3 = st.columns([5, 4, 3])

        with act_c1:
            badge_label = current_user.get("badge", "EMS-4092") if current_user else "EMS-4092"
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%;">
                    <span class="mr-status-pill" title="Operator: {badge_label}">
                        <span class="mr-status-dot"></span>
                        ONLINE &bull; STEP #{simulation_step}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with act_c2:
            if show_dispatch_btn:
                if st.button("Dispatch Center ›", type="primary", use_container_width=True):
                    try:
                        st.switch_page("pages/06_Dispatch_Center.py")
                    except Exception:
                        pass
            elif current_user:
                st.markdown(
                    f"""
                    <div style="font-size: 0.75rem; color: #334155; text-align: right; line-height: 1.25;">
                        <strong>{current_user.get('badge', 'EMS-4092')}</strong><br>
                        <span style="color: #64748B;">{current_user.get('name', 'Operator')}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with act_c3:
            if current_user:
                if st.button("Sign Out", key=f"logout_{title.replace(' ', '_')}", use_container_width=True):
                    logout_user()


def render_kpi_card(
    title: str = "",
    value: Any = 0,
    subtext: str = "",
    pill_text: str = "",
    pill_type: str = "green",
    icon_symbol: str = "●",
    icon_bg: str = "#EBF8F6",
    icon_color: str = "#0F9D92",
    **kwargs: Any,
) -> None:
    """Render a Dribbble-grade SaaS metric card with flexible keyword/positional arguments."""
    # Support alternate parameter names (e.g. label, footer_text)
    card_title = title or kwargs.get("label", "")
    card_subtext = subtext or kwargs.get("footer_text", "")

    # If 4th positional argument was an accent color hex (e.g. "#0D1B2A")
    if pill_text and str(pill_text).startswith("#"):
        icon_color = str(pill_text)
        icon_bg = f"{icon_color}14" if len(icon_color) == 7 else "#F1F5F9"
        pill_text = kwargs.get("pill_text", "")

    # Also handle accent_color / color in kwargs
    if "accent_color" in kwargs:
        icon_color = kwargs["accent_color"]
        icon_bg = f"{icon_color}14" if len(icon_color) == 7 else icon_bg
    elif "color" in kwargs:
        icon_color = kwargs["color"]
        icon_bg = f"{icon_color}14" if len(icon_color) == 7 else icon_bg

    pill_html = ""
    if pill_text and not str(pill_text).startswith("#"):
        pill_cls = f"mr-pill-{pill_type}"
        pill_html = f'<span class="mr-pill-badge {pill_cls}">{pill_text}</span>'

    st.markdown(
        f"""
        <div class="mr-kpi-card">
            <div class="mr-kpi-header">
                <span class="mr-kpi-label">{card_title}</span>
                <span class="mr-kpi-icon-badge" style="background-color: {icon_bg}; color: {icon_color};">
                    {icon_symbol}
                </span>
            </div>
            <div class="mr-kpi-value">{value}</div>
            <div class="mr-kpi-footer">
                {pill_html}
                <span style="color: #64748B; font-size: 0.72rem;">{card_subtext}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Backward-compatible alias
def render_metric_card(
    label: str,
    value: Any,
    subtext: str = "",
    color: str = "#0F172A",
    **kwargs: Any,
) -> None:
    """Backward-compatible alias for render_kpi_card."""
    render_kpi_card(title=label, value=value, subtext=subtext, icon_color=color, **kwargs)


def render_header(
    title: str = "Overview Dashboard",
    subtitle: str = "Emergency Fleet & Dispatch Operations",
    badge_text: str = "",
    **kwargs: Any,
) -> None:
    """Backward-compatible alias for render_command_bar."""
    render_command_bar(title=title, subtitle=subtitle, **kwargs)


def render_priority_badge(priority: str) -> str:
    """Return HTML for an emergency incident priority badge."""
    p_lower = priority.lower()
    badge_cls = f"mr-badge-{p_lower}" if p_lower in ["critical", "high", "medium", "low"] else "mr-badge-low"
    return f'<span class="mr-badge {badge_cls}">{priority.upper()}</span>'


def render_status_badge(status: str) -> str:
    """Return HTML for an operational status badge."""
    s_lower = status.lower()
    if s_lower == "available":
        return '<span class="mr-badge mr-badge-available">AVAILABLE</span>'
    if s_lower == "busy":
        return '<span class="mr-badge mr-badge-busy">EN ROUTE</span>'
    if s_lower == "pending":
        return '<span class="mr-badge mr-badge-critical">PENDING</span>'
    if s_lower == "assigned":
        return '<span class="mr-badge mr-badge-medium">DISPATCHED</span>'
    if s_lower == "completed":
        return '<span class="mr-badge mr-badge-available">RESOLVED</span>'
    return f'<span class="mr-badge mr-badge-low">{status.upper()}</span>'


def render_disclaimer() -> None:
    """Render a compact, professional educational simulation disclaimer."""
    st.markdown(
        """
        <div class="mr-footer-disclaimer">
            <div>
                <strong>Simulation Notice:</strong> MediRoute is an educational Design &amp; Analysis of Algorithms (DAA)
                system. All road topologies, travel times, and incident telemetry are synthetic.
            </div>
            <div>
                Engine: <code>Dijkstra SSSP + Greedy Heuristics</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
