import streamlit as st
from src.supabase_client import get_supabase


def show_auth():

    supabase = get_supabase()

    st.title("FinPilot AI")

    login_tab, signup_tab = st.tabs(
        ["Login", "Create Account"]
    )

    # -------------------------
    # LOGIN
    # -------------------------

    with login_tab:

        st.subheader("Welcome back")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary"
        ):

            if not email or not password:

                st.warning(
                    "Please enter your email and password."
                )

            else:

                try:

                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password
                        }
                    )

                    st.session_state.user = response.user

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        "Invalid email or password."
                    )

    # -------------------------
    # SIGN UP
    # -------------------------

    with signup_tab:

        st.subheader("Create your account")

        signup_email = st.text_input(
            "Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account"
        ):

            if not signup_email or not signup_password:

                st.warning(
                    "Please fill in all fields."
                )

            elif signup_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(signup_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                try:

                    response = supabase.auth.sign_up(
                        {
                            "email": signup_email,
                            "password": signup_password
                        }
                    )

                    st.success(
                        "Account created! Check your email to verify your account."
                    )

                except Exception as error:

                    st.error(
                        "Could not create the account."
                    )