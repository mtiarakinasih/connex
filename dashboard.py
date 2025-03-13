import streamlit as st
from PIL import Image
import pandas as pd

# Custom CSS untuk tampilan
def custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Monda:wght@400;700&family=Roboto:wght@300&display=swap');

        /* Main background */
        .stApp {
            background-color: #E5E5CB;
        }

        /* Main menu title, headers, and text */
        h1, h2, h3, h4, h5, h6, p {
            color: #1A120B;
            font-family: 'Monda', sans-serif;
        }

        /* Sidebar customization */
        [data-testid="stSidebar"] {
            background-color: #201414;
        }

        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label {
            color: #E5E5CB;
            font-family: 'Monda', sans-serif;
        }

        /* Button styling */
        div.stButton > button {
            background-color: #D5CEA3 !important; /* Warna latar */
            color: #3C2A21 !important; /* Warna teks */
            font-size: 16px !important;
            font-family: 'Monda', sans-serif !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            border: none !important;
            transition: 0.3s;
        }

        /* Hover effect */
        div.stButton > button:hover {
            background-color: #A67B5B !important;
            color: #E5E5CB !important;
        }

        /* Warna tombol Logout di sidebar */
        [data-testid="stSidebar"] .stButton > button {
            background-color: #E74C3C !important;
            color: white !important;
            font-size: 16px !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
        }

        /* Hover tombol Logout */
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #C0392B !important;
        }

        /* Logout button positioning */
        .logout-button {
            position: absolute;
            bottom: 20px;
            width: 80%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def dashboard_page():
    custom_css()

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Anda belum login. Silakan login terlebih dahulu.")
        st.session_state.page = "login"
        st.experimental_rerun()

    # Bagian Header dengan Logo
    col1, col2 = st.columns([5, 1]) 
    with col1:
        st.markdown("<h1 style='color: #201414; font-family: Monda, sans-serif;'>Dashboard</h1>", unsafe_allow_html=True)
    with col2:
        st.image("connex.png", use_container_width=True) 

    # **Ucapan Selamat Datang & Instruksi** (Langsung di bawah Dashboard)
    username = st.session_state.get("username", "User")  # Ambil username dari session_state
    st.markdown(f"<h3 style='color: #1A120B; margin-top: -10px;'>Selamat Datang, {username}👋</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #3C2A21; font-size: 16px;'>Silahkan pilih menu untuk konfigurasi:</p>", unsafe_allow_html=True)

    # Sidebar User Info
    st.sidebar.title("ℹ️ Info User")
    if "username" in st.session_state and "ip" in st.session_state:
        st.sidebar.write(f"👤 **Identity:** {st.session_state.identity}")
        st.sidebar.write(f"🌍 **MikroTik IP:** {st.session_state.ip}")

    # Menu Konfigurasi
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛠️ Basic Config", key="basic"):
            st.session_state.page = "basic"
            st.rerun()

        if st.button("🌐 Hotspot", key="hotspot"):
            st.session_state.page = "hotspot"
            st.rerun()

    with col2:
        if st.button("📶 Simple Queue", key="simpleq"):
            st.session_state.page = "simpleq"
            st.rerun()

        if st.button("🛑 Firewall", key="firewall"):
            st.session_state.page = "firewall"
            st.rerun()

    # Spacer biar tombol logout turun ke bawah
    for _ in range(20):
        st.sidebar.write("")  

    # Tombol Logout di Paling Bawah
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.success("✅ Logout berhasil. Kembali ke halaman login.")
        st.rerun()

# **Jalankan halaman**
if __name__ == "__main__":
    dashboard_page()
