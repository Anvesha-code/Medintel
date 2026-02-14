import streamlit as st
from utils.session_state import init_session_state
from utils.api_client import supabase_login, supabase_signup
from components.layout import render_layout

# --------------------------------------------------
# App Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="MedIntel",
    page_icon="🩺",
    layout="wide"
)

# --------------------------------------------------
# ✅ INIT SESSION STATE (CALL IT!)
# --------------------------------------------------
init_session_state()

# --------------------------------------------------
# App Header (GLOBAL)
# --------------------------------------------------
st.markdown(
    "<h1 style='margin-bottom:0'>🩺 MedIntel</h1>"
    "<p style='color:gray;margin-top:0'>AI-powered medical document intelligence</p>",
    unsafe_allow_html=True
)

# ==================================================
# 🔐 AUTH GATE
# ==================================================
if not st.session_state.logged_in:
    st.subheader("🔐 Login / Signup")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    # ---------- LOGIN ----------
    with col1:
        if st.button("Login"):
            try:
                auth_response = supabase_login(email, password)

                st.session_state.token = auth_response["session"]["access_token"]
                st.session_state.user_id = auth_response["user"]["id"]
                st.session_state.logged_in = True

                st.success("✅ Login successful")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Login failed: {e}")

    # ---------- SIGNUP ----------
    with col2:
        if st.button("Signup"):
            try:
                auth_response = supabase_signup(email, password)

                session = auth_response.get("session")

                # 🔐 Email confirmation enabled
                if not session:
                    st.success(
                        "✅ Signup successful!\n\n"
                        "📩 Please confirm your email, then login."
                    )
                    st.stop()

                # ✅ Auto-login
                st.session_state.token = session["access_token"]
                st.session_state.user_id = auth_response["user"]["id"]
                st.session_state.logged_in = True

                st.success("✅ Signup successful")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Signup failed: {e}")

# ==================================================
# 🚀 FULL MEDINTEL APP (POST LOGIN)
# ==================================================
else:
    st.success(f"Logged in as: {st.session_state.user_id}")

    # 🔹 Logout
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    render_layout()
