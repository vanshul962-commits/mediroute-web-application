"""Unit tests for MediRoute authentication and role access."""

import pytest
from ui.auth import (
    AUTHORIZED_USERS,
    AUTH_SESSION_KEY,
    get_current_user,
    is_authenticated,
    login_user,
    logout_user,
)


def test_authorized_users_credentials():
    """Verify default dispatch personnel credentials exist."""
    assert "dispatcher" in AUTHORIZED_USERS
    assert AUTHORIZED_USERS["dispatcher"]["password"] == "mediroute2026"
    assert "admin" in AUTHORIZED_USERS


def test_session_auth_lifecycle(monkeypatch):
    """Verify login, user retrieval, and logout lifecycle."""
    mock_session = {}

    import streamlit as st
    monkeypatch.setattr(st, "session_state", mock_session)
    monkeypatch.setattr(st, "rerun", lambda: None)

    assert not is_authenticated()
    assert get_current_user() is None

    # Perform login
    login_user(
        username="dispatcher",
        name="Officer R. Martinez",
        role="Senior Dispatch Controller",
        badge="EMS-4092",
        shift="Day Operations",
    )

    assert is_authenticated()
    user = get_current_user()
    assert user is not None
    assert user["badge"] == "EMS-4092"
    assert user["username"] == "dispatcher"

    # Logout
    logout_user()
    assert not is_authenticated()
    assert get_current_user() is None
