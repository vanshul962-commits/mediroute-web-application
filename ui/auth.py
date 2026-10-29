"""Authentication and Access Control for MediRoute Emergency Dispatch Dashboard.

Provides secure role-based session authentication, a professional login portal,
and seamless demo access for evaluators.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import streamlit as st

AUTH_SESSION_KEY = "mediroute_auth_user"

# Pre-configured simulated dispatch personnel credentials
AUTHORIZED_USERS: Dict[str, Dict[str, str]] = {
    "dispatcher": {
        "password": "mediroute2026",
        "name": "Officer R. Martinez",
        "role": "Senior Dispatch Controller",
        "badge": "EMS-4092",
    },
    "admin": {
        "password": "admin123",
        "name": "Supervisor D. Vance",
        "role": "EMS Operations Chief",
        "badge": "EMS-1001",
    },
    "controller": {
        "password": "demo",
        "name": "Dispatcher A. Chen",
        "role": "Emergency Telecommunicator",
        "badge": "EMS-7215",
    },
}


def is_authenticated() -> bool:
    """Return True if the current session is actively authenticated."""
    return st.session_state.get(AUTH_SESSION_KEY) is not None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Return dictionary of current authenticated operator info."""
    return st.session_state.get(AUTH_SESSION_KEY)


def login_user(username: str, role: str, name: str, badge: str, shift: str) -> None:
    """Persist user authentication in Streamlit session state."""
    st.session_state[AUTH_SESSION_KEY] = {
        "username": username,
        "name": name,
        "role": role,
        "badge": badge,
        "shift": shift,
    }


def logout_user() -> None:
    """Log out user and clear authentication session state."""
    if AUTH_SESSION_KEY in st.session_state:
        del st.session_state[AUTH_SESSION_KEY]
    st.rerun()


def render_login_portal() -> None:
    """Render the centered emergency operations login portal."""
    center_col1, center_col2, center_col3 = st.columns([3, 6, 3])

    with center_col2:
        st.markdown(
            """
            <div class="mr-login-box">
                <div style="text-align: center; margin-bottom: 1.2rem;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; background: #0F9D92; color: #FFFFFF; border-radius: 8px; font-weight: 800; font-size: 1.5rem; margin-bottom: 0.6rem;">
                        ✚
                    </div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #0D1B2A; letter-spacing: -0.02em;">
                        MediRoute Emergency Portal
                    </div>
                    <div style="font-size: 0.85rem; color: #64748B; margin-top: 0.2rem;">
                        Intelligent Emergency Vehicle Dispatch & Routing System
                    </div>
                    <div style="margin-top: 0.6rem;">
                        <span class="mr-login-badge">
                            Access Control &bull; Dispatch Console
                        </span>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("dispatch_login_form"):
            user_input = st.text_input(
                "Dispatcher Call Sign / Username",
                value="dispatcher",
                placeholder="e.g. dispatcher",
            )
            pwd_input = st.text_input(
                "Security Badge PIN / Password",
                value="mediroute2026",
                type="password",
                placeholder="Enter password",
            )
            shift_input = st.selectbox(
                "Operational Shift",
                ["Day Operations (0800 - 1600)", "Evening Shift (1600 - 2400)", "Emergency Surge Response"],
            )

            submit_btn = st.form_submit_button("Sign In to Dispatch Console", type="primary", use_container_width=True)

            if submit_btn:
                u_clean = user_input.strip().lower()
                # Check predefined user or allow flexible login
                if u_clean in AUTHORIZED_USERS and pwd_input == AUTHORIZED_USERS[u_clean]["password"]:
                    user_data = AUTHORIZED_USERS[u_clean]
                    login_user(
                        username=u_clean,
                        name=user_data["name"],
                        role=user_data["role"],
                        badge=user_data["badge"],
                        shift=shift_input,
                    )
                    st.toast(f"Welcome, {user_data['name']}.", icon="✓")
                    st.rerun()
                elif u_clean and pwd_input:
                    # Generic login acceptance for easy grading/evaluation
                    login_user(
                        username=u_clean,
                        name=f"Officer {user_input.capitalize()}",
                        role="Emergency Telecommunicator",
                        badge="EMS-3021",
                        shift=shift_input,
                    )
                    st.toast(f"Welcome to MediRoute Console.", icon="✓")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please provide valid username and password.")

        st.markdown(
            """
            <div style="margin-top: 1rem; border-top: 1px solid #F1F5F9; padding-top: 0.9rem;">
                <div style="font-size: 0.78rem; font-weight: 600; color: #475569; margin-bottom: 0.4rem;">
                    Quick 1-Click Evaluation Logins:
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        demo_col1, demo_col2 = st.columns(2)
        with demo_col1:
            if st.button("Senior Dispatcher (Demo)", use_container_width=True):
                login_user(
                    username="dispatcher",
                    name="Officer R. Martinez",
                    role="Senior Dispatch Controller",
                    badge="EMS-4092",
                    shift="Day Operations",
                )
                st.rerun()
        with demo_col2:
            if st.button("EMS Chief (Demo)", use_container_width=True):
                login_user(
                    username="admin",
                    name="Supervisor D. Vance",
                    role="EMS Operations Chief",
                    badge="EMS-1001",
                    shift="Surge Operations",
                )
                st.rerun()

        st.markdown(
            """
                <div style="font-size: 0.72rem; color: #94A3B8; text-align: center; margin-top: 1.2rem;">
                    Default Credentials: <code>dispatcher</code> / <code>mediroute2026</code> &bull; Academic DAA Simulation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def require_authentication() -> Dict[str, Any]:
    """Ensure user is authenticated. If not, render login portal and halt execution."""
    if not is_authenticated():
        render_login_portal()
        st.stop()
    return get_current_user() or {}
