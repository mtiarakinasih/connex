import streamlit as st
import paramiko
import re

# 🔹 Fungsi eksekusi command di MikroTik
def execute_mikrotik_command(command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=st.session_state.ip, port=st.session_state.port, 
                       username=st.session_state.username, password=st.session_state.password)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        client.close()
        return output.strip()
    except Exception as e:
        st.error(f"❌ Gagal mengeksekusi perintah: {e}")
        return None

# 🔹 Ambil daftar interface yang aktif
def get_active_interfaces():
    command = "/interface print terse where running"
    output = execute_mikrotik_command(command)
    interfaces = []
    if output:
        for line in output.split("\n"):
            match = re.search(r"name=([\w\d-]+)", line)
            if match:
                interfaces.append(match.group(1))
    return interfaces

# 🔥 **Halaman Simple Queue**
def queue_page():
    st.markdown('<div class="title">Simple Queue Dashboard</div>', unsafe_allow_html=True)
    st.markdown("""
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
                font-family: 'Monda', sans-serif
                    }
            hr {
            border: none;
            height: 3px;
            background-color: 1A120B; /* Ganti warna sesuai keinginan */
        }

        </style>
        """, unsafe_allow_html=True)

    # Cek apakah user sudah login
    if not all(k in st.session_state for k in ["ip", "port", "username", "password"]):
        st.error("Anda belum login! Silakan login terlebih dahulu.")
        st.stop()

    # **Ambil daftar interface yang aktif**
    interfaces = get_active_interfaces()
    if not interfaces:
        st.warning("⚠️ Tidak ada interface yang aktif.")
        return

    # **Dropdown untuk pilih interface**
    selected_interface = st.selectbox("Pilih Interface:", interfaces)

    # **Input batasan bandwidth**
    upload_limit = st.text_input("Masukkan Target Upload (Contoh: 1M, 512k, 1000000):", placeholder="1M", key="upload_limit")
    download_limit = st.text_input("Masukkan Target Download (Contoh: 5M, 1000k, 5000000):", placeholder="5M", key="download_limit")


    # **Tombol Set Limit**
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("✔️ Terapkan"):
            if not upload_limit or not download_limit:
                st.error("⚠️ Harap masukkan batasan bandwidth upload dan download!")
            else:
                # Tambahkan Simple Queue untuk interface yang dipilih
                command = f"/queue simple add name=Limit-{selected_interface} target={selected_interface} max-limit={upload_limit}/{download_limit}"
                execute_mikrotik_command(command)
                st.success(f"✅ Interface {selected_interface} dibatasi: Upload {upload_limit}, Download {download_limit}")
                st.rerun()

    # **Tombol Hapus Batasan**
    with col1:
        if st.button("✖️ Hapus"):
            command = f"/queue simple remove [find where name=Limit-{selected_interface}]"
            execute_mikrotik_command(command)
            
            # 🔹 Hapus nilai input dari session state
            del st.session_state["upload_limit"]
            del st.session_state["download_limit"]
            
            st.success(f"✅ Batasan di {selected_interface} dihapus, semua user bebas!")
            st.rerun()

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
    queue_page()
