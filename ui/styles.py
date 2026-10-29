"""Professional UI Styling and Design System for MediRoute Emergency Dashboard.

Enterprise-grade command-and-control SaaS interface inspired by modern fleet-telemetry,
logistics, and emergency operations platforms (e.g. NexRoute, Samsara, Datadog).
"""

from __future__ import annotations

PROFESSIONAL_CSS = """
<style>
/* 1. Eliminate Excessive Streamlit Blank Space Above Header */
.block-container,
.main > .block-container,
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding-top: 0.35rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    margin-top: 0 !important;
    max-width: 100% !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    height: 1.25rem !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stVerticalBlock"] > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Prevent horizontal overflow globally */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}

/* Hide Streamlit Deploy Button, Toolbar, and Cloud Badges */
.stDeployButton,
[data-testid="stDeployButton"],
[data-testid="stToolbarActions"],
[data-testid="stDecoration"],
[data-testid="stHeader"] .stDeployButton,
#MainMenu {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    opacity: 0 !important;
}

/* 2. Color Palette & Typography */
:root {
    --mr-navy-dark: #0F172A;
    --mr-navy-card: #1E293B;
    --mr-teal-primary: #0F9D92;
    --mr-teal-hover: #0C8279;
    --mr-teal-light: #EBF8F6;
    --mr-bg-app: #F8FAFC;
    --mr-card-bg: #FFFFFF;
    --mr-text-primary: #0F172A;
    --mr-text-secondary: #475569;
    --mr-text-muted: #64748B;
    --mr-border: #E2E8F0;
    --mr-border-light: #F1F5F9;
    --mr-red-critical: #DC2626;
    --mr-red-light: #FEE2E2;
    --mr-green-success: #16A34A;
    --mr-green-light: #DCFCE7;
    --mr-amber-warning: #D97706;
    --mr-amber-light: #FEF3C7;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: var(--mr-text-primary);
}

.stApp {
    background-color: var(--mr-bg-app);
}

/* 3. Top Command Bar */
.mr-top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #FFFFFF;
    border: 1px solid var(--mr-border);
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}

.mr-brand-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.mr-brand-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    background: #0F9D92;
    color: #FFFFFF;
    border-radius: 8px;
    font-weight: 800;
    font-size: 1.15rem;
}

.mr-brand-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--mr-navy-dark);
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.mr-brand-sub {
    font-size: 0.75rem;
    color: var(--mr-text-muted);
    font-weight: 500;
    margin-top: 0.1rem;
}

.mr-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background-color: #F0FDF4;
    color: #166534;
    border: 1px solid #BBF7D0;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.mr-status-dot {
    width: 7px;
    height: 7px;
    background-color: #16A34A;
    border-radius: 50%;
    animation: mr-pulse-dot 2s infinite;
}

@keyframes mr-pulse-dot {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.8; }
}

/* 4. Dribbble-Grade SaaS KPI Metric Cards */
.mr-kpi-card {
    background-color: #FFFFFF;
    border: 1px solid var(--mr-border);
    border-radius: 10px;
    padding: 0.95rem 1.1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    position: relative;
    overflow: hidden;
}

.mr-kpi-card:hover {
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    transform: translateY(-1px);
    border-color: #CBD5E1;
}

.mr-kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}

.mr-kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--mr-text-muted);
    letter-spacing: 0.02em;
}

.mr-kpi-icon-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 6px;
    font-size: 0.8rem;
}

.mr-kpi-value {
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--mr-navy-dark);
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin-bottom: 0.35rem;
}

.mr-kpi-footer {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.72rem;
    color: var(--mr-text-secondary);
}

.mr-pill-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.1rem 0.45rem;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 600;
}

.mr-pill-green {
    background-color: #DCFCE7;
    color: #15803D;
}

.mr-pill-red {
    background-color: #FEE2E2;
    color: #B91C1C;
}

.mr-pill-amber {
    background-color: #FEF3C7;
    color: #B45309;
}

.mr-pill-blue {
    background-color: #EFF6FF;
    color: #1D4ED8;
}

.mr-pill-gray {
    background-color: #F1F5F9;
    color: #475569;
}

/* 5. Clean Panels and Cards */
.mr-panel-box {
    background-color: #FFFFFF;
    border: 1px solid var(--mr-border);
    border-radius: 10px;
    padding: 1rem 1.15rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}

.mr-panel-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--mr-border-light);
    padding-bottom: 0.55rem;
    margin-bottom: 0.75rem;
}

.mr-panel-heading {
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--mr-navy-dark);
    letter-spacing: -0.01em;
}

.mr-panel-caption {
    font-size: 0.72rem;
    color: var(--mr-text-muted);
}

/* 6. Incident Queue Cards */
.mr-incident-item {
    background-color: #FFFFFF;
    border: 1px solid var(--mr-border);
    border-radius: 8px;
    padding: 0.75rem 0.95rem;
    margin-bottom: 0.55rem;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.mr-incident-item:hover {
    border-color: #94A3B8;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
}

.mr-incident-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
}

.mr-incident-code {
    font-weight: 700;
    font-size: 0.88rem;
    color: var(--mr-navy-dark);
}

.mr-incident-place {
    font-size: 0.8rem;
    color: #334155;
    margin-bottom: 0.2rem;
}

.mr-incident-narrative {
    font-size: 0.75rem;
    color: var(--mr-text-muted);
    line-height: 1.35;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* 7. Button Styling */
button[kind="primary"] {
    background-color: #0F9D92 !important;
    border-color: #0F9D92 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
}

button[kind="primary"]:hover {
    background-color: #0C8279 !important;
    border-color: #0C8279 !important;
}

button[kind="secondary"] {
    background-color: #FFFFFF !important;
    border-color: #E2E8F0 !important;
    color: #334155 !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
}

button[kind="secondary"]:hover {
    border-color: #CBD5E1 !important;
    background-color: #F8FAFC !important;
}

/* 8. Modern Badges */
.mr-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.mr-badge-critical {
    background-color: #FEE2E2;
    color: #DC2626;
    border: 1px solid #FECACA;
}

.mr-badge-high {
    background-color: #FEF3C7;
    color: #D97706;
    border: 1px solid #FDE68A;
}

.mr-badge-medium {
    background-color: #EBF8F6;
    color: #0F9D92;
    border: 1px solid #B8EBE2;
}

.mr-badge-low {
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

.mr-badge-available {
    background-color: #DCFCE7;
    color: #16A34A;
    border: 1px solid #BBF7D0;
}

.mr-badge-busy {
    background-color: #FEE2E2;
    color: #DC2626;
    border: 1px solid #FECACA;
}

/* 9. Login Box */
.mr-login-box {
    background-color: #FFFFFF;
    border: 1px solid var(--mr-border);
    border-radius: 12px;
    padding: 2.2rem 2.4rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    margin-top: 1.5rem;
}

/* 10. Educational Disclaimer Footer */
.mr-footer-disclaimer {
    border-top: 1px solid var(--mr-border);
    padding-top: 0.75rem;
    margin-top: 1.5rem;
    font-size: 0.72rem;
    color: var(--mr-text-muted);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
}

/* 11. Responsive Grid & Mobile Breakpoints */
@media (max-width: 1100px) {
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.65rem !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: calc(33.333% - 0.65rem) !important;
        flex: 1 1 calc(33.333% - 0.65rem) !important;
    }
}

@media (max-width: 768px) {
    .block-container,
    .main > .block-container,
    [data-testid="stAppViewContainer"] > .main > .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-top: 0.35rem !important;
    }
    .mr-top-bar {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 0.6rem !important;
        padding: 0.75rem 1rem !important;
    }
    .mr-kpi-value {
        font-size: 1.4rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: calc(50% - 0.5rem) !important;
        flex: 1 1 calc(50% - 0.5rem) !important;
    }
}

@media (max-width: 480px) {
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }
}
</style>
"""


def apply_custom_styles() -> None:
    """Inject the professional SaaS dashboard styles."""
    import streamlit as st

    st.markdown(PROFESSIONAL_CSS, unsafe_allow_html=True)
