import streamlit as st
import paramiko

def login_page():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Monda:wght@400;700&display=swap');
            
            .title {
                color: #1A120B;
                font-size: 40px;
                font-family: 'Monda', sans-serif;
                font-weight: 700;  /* Menetapkan bobot font ke bold */
                text-align: center;  /* Memusatkan teks */
            }
            
            .subheading {
                color: #3C2A21;  /* Warna teks */
                font-size: 15px;
                font-family: 'Monda', sans-serif;
                font-weight: 400;  /* Menetapkan bobot font ke normal */
                text-align: center;  /* Memusatkan teks */
                margin-top: 10px;  /* Memberi jarak sedikit antara judul dan pesan */
            }
        </style>
        """, unsafe_allow_html=True)

    # Menampilkan judul dan pesan di bawahnya
    st.markdown('<div class="title">Connect With Connex</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheading">Welcome back! Please login to your Mikrotik 🛜</div>', unsafe_allow_html=True)


    # Tambahkan CSS untuk latar belakang dan form
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Monda:wght@400;700&display=swap');
            
            .stApp {
                background-color: #E5E5CB;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
                
            /* Main menu title, headers, and text */
            h1, h2, h3, h4, h5, h6, p {
                color: #201414 ;
                font-family: 'Monda', sans-serif;
            }
                
            .login-container {
                display: flex;
                width: 80%;
                max-width: 1000px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            .left-panel {
                background-color: #3C2A21;
                color: #E5E5CB;
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 2rem;
            }
            .right-panel {
                background-color: #E5E5CB;
                color: #3C2A21;
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 2rem;
            }
            .stTextInput > div > div > input {
                background-color: #E5E5CB;
                color: #3C2A21;
                border: 1px solid #3C2A21;
                border-radius: 0.375rem;
                padding: 0.5rem;
            }
            .stForm {
                background-color: #E5E5CB;
                padding: 20px;
                border-radius: 10px;
            }
           .stButton > button {
                background-color: #D5CEA3 !important;
                color: white !important;
                border-radius: 8px !important;
                padding: 8px 16px !important;
                border: none !important;
                transition: 0.3s !important;
            } 
        .stButton > button:hover {
            background-color: #A67B5B !important;
            color: #D5CEA3 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    #Form Login 
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Monda:wght@400;700&display=swap');
            
            .stTextInput input {
                color: #1A120B;  /* Ganti dengan warna yang kamu inginkan */
                font-family: 'Monda', sans-serif;
                font-weight: 600;  /* Semi-Bold */
            }
            .stPassword input {
                color: #1A120B;  /* Ganti dengan warna yang kamu inginkan */
                font-family: 'Monda', sans-serif;
                font-weight: 600;  /* Semi-Bold */
            }
            .stTextInput label {
                color: #1A120B;  /* Ganti dengan warna label */
                font-family: 'Monda', sans-serif;
                font-weight: 600;  /* Semi-Bold */
            }
        </style>
        """, unsafe_allow_html=True)


    ip = st.text_input("Mikrotik IP:")
    username = st.text_input("Username:")
    password = st.text_input("Password (Opsional):", type="password")  # Sekarang opsional

    if st.button("Login"):
        if not ip or not username:  # Hanya IP & Username yang wajib
            st.error("⚠️ Harap isi IP dan Username!")
            return

        # Pisahkan IP dan port jika ada
        if ':' in ip:
            parts = ip.split(':')
            if len(parts) != 2 or not parts[1].isdigit():
                st.error("Port harus berupa angka yang valid!")
                return
            host, port = parts[0], int(parts[1])
        else:
            host, port = ip, 22  # Default SSH port

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Koneksi tanpa password jika password kosong
            if password:
                client.connect(hostname=host, port=port, username=username, password=password)
            else:
                client.connect(hostname=host, port=port, username=username)

            stdin, stdout, stderr = client.exec_command("/system identity print")
            identity = stdout.read().decode().strip().split(":")[-1].strip()
            client.close()

            st.session_state.logged_in = True
            st.session_state.page = "dashboard"
            st.session_state.identity = identity
            st.session_state.ip = host
            st.session_state.port = port
            st.session_state.username = username
            st.session_state.password = password

            st.success("✅ Login berhasil! Berpindah ke Dashboard...")
            st.rerun()

        except paramiko.AuthenticationException:
            st.error("❌ Login gagal! Username atau password salah.")
        except paramiko.SSHException as e:
            st.error(f"❌ SSH Error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {str(e)}")
