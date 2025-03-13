import streamlit as st
from login import login_page
from dashboard import dashboard_page
from basic import basic_page
from simpleq import queue_page
from hotspot import hotspot_page
from firewall import firewall_page

# Initialize session states
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Jika belum login, arahkan ke halaman login
if not st.session_state.logged_in:
    st.session_state.page = "login"

# Navigasi berdasarkan session state
if st.session_state.page == "dashboard":
    dashboard_page()
elif st.session_state.page == "basic":
    basic_page()
elif st.session_state.page == "simpleq":
    queue_page()
elif st.session_state.page == "hotspot":
    hotspot_page()
elif st.session_state.page == "firewall":
    firewall_page()
else:
    login_page()
