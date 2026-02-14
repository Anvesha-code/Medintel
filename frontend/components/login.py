import streamlit as st
import requests




SUPABASE_URL="https://tvvnsweuuajlhhvbhzmo.supabase.co"
SUPABASE_ANON_KEY="sb_publishable_Wo4XfmkeJYa9p24Hvf9Viw_vM6bHnzz"

def login_ui():
    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Email and password required")
            return

        response = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": email,
                "password": password
            }
        )

        if not response.ok:
            st.error("Invalid credentials")
            return

        data = response.json()

        st.session_state.access_token = data["access_token"]
        st.session_state.user_id = data["user"]["id"]
        st.session_state.logged_in = True

        st.success("Login successful")
        st.rerun()
