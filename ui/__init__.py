"""UI package for MediRoute."""

from ui.auth import (
    get_current_user,
    is_authenticated,
    login_user,
    logout_user,
    render_login_portal,
    require_authentication,
)
from ui.components import (
    render_command_bar,
    render_disclaimer,
    render_header,
    render_kpi_card,
    render_metric_card,
    render_priority_badge,
    render_status_badge,
)
from ui.styles import apply_custom_styles

__all__ = [
    "apply_custom_styles",
    "render_command_bar",
    "render_header",
    "render_kpi_card",
    "render_metric_card",
    "render_priority_badge",
    "render_status_badge",
    "render_disclaimer",
    "is_authenticated",
    "get_current_user",
    "login_user",
    "logout_user",
    "render_login_portal",
    "require_authentication",
]
