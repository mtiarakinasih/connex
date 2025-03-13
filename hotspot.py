import streamlit as st
import paramiko
import pandas as pd
import time
import plotly.express as px

# 🔹 Fungsi eksekusi command di MikroTik
def run_mikrotik_command(command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=st.session_state.ip,
            port=st.session_state.port,
            username=st.session_state.username,
            password=st.session_state.password
        )

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error_output = stderr.read().decode().strip()
        client.close()

        if error_output:
            st.error(f"Terjadi kesalahan dari MikroTik: {error_output}")

        return output
    except Exception as e:
        st.error(f"Gagal menjalankan perintah: {e}")
        return ""

# 🔹 Fungsi mendapatkan pengguna aktif
def get_active_users():
    output = run_mikrotik_command("/ip hotspot active print terse")
    users = []

    for line in output.split("\n"):
        data = {}
        for item in line.split():
            if "=" in item:
                key, value = item.split("=", 1)
                data[key] = value
        if data:
            users.append({
                "Username": data.get("user", "Unknown"),
                "IP Address": data.get("address", "Unknown"),
                "MAC Address": data.get("mac-address", "Unknown"),
                "Uptime": data.get("uptime", "Unknown"),
            })

    return pd.DataFrame(users)

# 🔥 **Halaman Hotspot Monitoring**
def hotspot_page():
    st.markdown('<div class="title">Mikrotik Hotspot Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Monda:wght@400;700&display=swap');
        .title {
                color: #1A120B;
                font-size: 40px;
                font-family: 'Monda', sans-serif;
                font-weight: 700;  /* Menetapkan bobot font ke bold */
                text-align: Left;  /* Memusatkan teks */
        }
        
       .subheader {
            color: #1A120B;
            font-size: 24px;
            font-family: 'Monda', sans-serif;
            font-weight: 600;
            text-align: left;
            margin-top: 20px;
        }
        .stTextInput > div > div > input::placeholder {
            color: #b8b8a9;  /* Warna */
            font-weight: bold;
        }
        .subheader {
            color: #1A120B;
            font-size: 24px;
            font-family: 'Monda', sans-serif;
            font-weight: 600;
            text-align: left;
            margin-top: 20px;
        }
        .stApp {
            background-color: #E5E5CB;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
                
        h1, h2, h3, h4, h5, h6, p {
            color: #1A120B;
            font-family: 'Monda', sans-serif;
        }

        .stTextInput > div > div > input {
            background-color: #E5E5CB;
            color: #3C2A21;
            border: 1px solid #3C2A21;
            border-radius: 0.375rem;
            padding: 0.5rem;
        }

        /* Tambahin buat button */
        .stButton>button {
            background-color: #D5CEA3;
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            border: none;
            transition: 0.3s;
        }

        .stButton>button:hover {
            background-color: #A67B5B;
            color: #D5CEA3;
        }
                
        .stTextInput input {
                color: #1A120B;  /* Ganti dengan warna yang kamu inginkan */
                font-family: 'Monda', sans-serif;
                font-weight: 600;  /* Semi-Bold */
        }
        div[data-baseweb="select"] input {
            color: #3C2A21 !important;
            background-color: #E5E5CB !important;
            font-size: 16px !important;
            font-weight: bold !important;
            font-family: 'Monda', sans-serif !important;
        }

        div[data-baseweb="option"] {
            color: #E5E5CB !important;
            background-color: #3C2A21 !important;
            font-size: 16px !important;
            font-family: 'Monda', sans-serif !important;
        }

        div[data-baseweb="select"] > div {
            color: #3C2A21 !important;
            background-color: #E5E5CB !important;
            font-family: 'Monda', sans-serif !important;
        }
    </style>
        """,
        unsafe_allow_html=True
    )

    
    # **Pengguna yang Terhubung**
    st.markdown('<div class="subheader">🔗 Pengguna yang Sedang Terhubung</div>', unsafe_allow_html=True)
    
    df_active_users = get_active_users()
    st.dataframe(df_active_users if not df_active_users.empty else pd.DataFrame(columns=["Username", "IP Address", "MAC Address", "Uptime"]))

    # **Grafik Pengguna Aktif**
    st.markdown('<div class="subheader">📊 Grafik Jumlah Pengguna Aktif</div>', unsafe_allow_html=True)
    active_users_count = len(df_active_users)
    chart_data = pd.DataFrame({"Waktu": [time.strftime("%H:%M:%S")], "Jumlah User": [active_users_count]})
    fig = px.line(chart_data, x="Waktu", y="Jumlah User", title="Grafik Pengguna Aktif", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# --- MODAL KONFIRMASI ---
    if "show_modal" not in st.session_state:
     st.session_state.show_modal = False

    if st.button("Tutup"):
        st.session_state.show_modal = True

    if st.session_state.show_modal:
        with st.expander("⚙️ Konfirmasi Tutup", expanded=True):
            st.warning("Apakah ingin melakukan konfigurasi lain?")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Ya, Konfigurasi Lagi"):
                    st.session_state.show_modal = False
                    st.session_state.page = "dashboard"
                    st.rerun()

            with col2:
                if st.button("❎ Tidak, Logout"):
                    st.session_state.clear()
                    st.success("Anda telah logout.")
                    st.rerun()

# **Jalankan halaman**
if __name__ == "__main__":
    hotspot_page()
