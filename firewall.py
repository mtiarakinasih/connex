import paramiko
import streamlit as st
import re
import pandas as pd

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

# 🔹 Ambil daftar domain dari Address List
def get_blocked_domains():
    command = "/ip firewall address-list print terse where list=BlockedSites"
    output = execute_mikrotik_command(command)

    blocked_domains = set()
    if output:
        for line in output.split("\n"):
            match = re.search(r"comment=([\w\d.-]+)", line)
            if match:
                blocked_domains.add(match.group(1))

    return list(blocked_domains)

# 🔹 Tambahkan domain ke Address List & Filter Rule (Drop)
def block_domain(domain):
    execute_mikrotik_command(f"/ip firewall address-list add list=BlockedSites address={domain} comment={domain}")
    execute_mikrotik_command(f"/ip firewall filter add chain=forward action=drop dst-address-list=BlockedSites protocol=tcp dst-port=80,443 comment={domain}")

# 🔹 Hapus domain dari Address List & Filter Rule (Accept)
def unblock_domain(domain):
    execute_mikrotik_command(f"/ip firewall address-list remove [find where list=BlockedSites and comment={domain}]")
    execute_mikrotik_command(f"/ip firewall filter remove [find where comment={domain} and action=drop]")

# 🔥 **Halaman Firewall**
def firewall_page():
    st.markdown('<div class="title">Firewall Configuration Dashboard</div>', unsafe_allow_html=True)
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

    # Cek login
    if "ip" not in st.session_state:
        st.error("Anda belum login! Silakan login terlebih dahulu.")
        st.stop()

    # Form input domain
    domain_input = st.text_input("Masukkan Domain:", placeholder="contoh: youtube.com")

    # **Tombol Set Rule**
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("✖️Drop"):
            if not domain_input:
                st.error("⚠️ Harap masukkan domain terlebih dahulu!")
            else:
                blocked_domains = get_blocked_domains()
                if domain_input not in blocked_domains:
                    block_domain(domain_input)
                    st.success(f"✅ {domain_input} berhasil diblokir!")
                else:
                    st.warning(f"⚠️ {domain_input} sudah ada dalam daftar blokir!")
                st.rerun()

    # **Garis pemisah**
    st.markdown("<hr style='border: 1px solid #1A120B; margin: 20px 0;'>", unsafe_allow_html=True)

    # **Daftar domain yang diblokir**
    st.markdown('<div class="subheader" style="text-align: center;">📋 Daftar Domain yang Diblokir</div>', unsafe_allow_html=True)
    blocked_domains = get_blocked_domains()

    if blocked_domains:
        col1, col2 = st.columns([6, 2])
        col1.markdown("**Domain**")
        col2.markdown("**Accept**")

        for domain in blocked_domains:
            col1, col2 = st.columns([6, 2])
            col1.write(domain)

            with col2:
                if st.button("✅", key=f"accept_{domain}"):
                    unblock_domain(domain)
                    st.success(f"✅ {domain} di-unblock!")
                    st.rerun()
    else:
        st.warning("Tidak ada domain yang diblokir.")

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
    firewall_page()
