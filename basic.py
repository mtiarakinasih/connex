import paramiko
import streamlit as st
import re
import pandas as pd

# Fungsi untuk mengeksekusi perintah MikroTik
def execute_mikrotik_command(command, return_output=False):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=st.session_state.ip, port=st.session_state.port, 
                       username=st.session_state.username, password=st.session_state.password)

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        client.close()

        if return_output:
            return output.strip()
    except Exception as e:
        st.error(f"❌ Gagal mengeksekusi perintah: {e}")
        return None

# Ambil daftar interface yang aktif
def get_active_interfaces():
    command = "/interface print terse where running"
    output = execute_mikrotik_command(command, return_output=True)
    interfaces = []
    if output:
        for line in output.split("\n"):
            match = re.search(r"name=([\w\d-]+)", line)
            if match:
                interfaces.append(match.group(1))
    return interfaces

# Cek apakah DHCP Client aktif pada interface
def get_dhcp_client_ip(interface):
    command = f"/ip dhcp-client print terse where interface={interface}"
    output = execute_mikrotik_command(command, return_output=True)
    if output:
        match = re.search(r"address=([\d./]+)", output)
        if match:
            return match.group(1)
    return None

# Tambahkan DHCP Client ke interface
def add_dhcp_client(interface):
    command = f"/ip dhcp-client add interface={interface} disabled=no"
    execute_mikrotik_command(command)
    st.session_state.dhcp_success = f"DHCP Client ditambahkan ke {interface}, coba periksa koneksi!"  # Simpan status ke session_state
    

# Ambil daftar IP Address
def fetch_ip_addresses():
    command = "/ip address print terse"
    output = execute_mikrotik_command(command, return_output=True)
    ip_list = []
    if output:
        for idx, line in enumerate(output.split("\n")):
            match = re.search(r"address=([\d./]+) network=([\d.]+) interface=([\w\d-]+)", line)
            if match:
                ip_list.append({
                    "Number": idx,
                    "IP Address": match.group(1),
                    "Network": match.group(2),
                    "Interface": match.group(3)
                })
    return pd.DataFrame(ip_list)

# Ambil daftar Route List dari MikroTik
def fetch_routes():
    command = "/ip route print terse"
    output = execute_mikrotik_command(command, return_output=True)  # FIX: Hapus parameter tambahan!

    if not output:
        st.error("❌ Tidak ada data yang dikembalikan dari MikroTik!")
        return pd.DataFrame(columns=["Flags", "Destination", "Gateway"])

    data = []
    lines = output.strip().split("\n")

    for line in lines:
        print("DEBUG:", line)  # Debugging untuk melihat format data dari MikroTik

        # Tangkap semua jenis route (DAC, AS, dll.)
        match = re.search(r"^\s*([\w\s-]*)\s*dst-address=([\d./]+).*?gateway=([\w\d.%/-]+)", line)
        if match:
            flags = match.group(1).strip() if match.group(1) else "-"  # Jika tidak ada flag, beri "-"
            dst_address = match.group(2)
            gateway = match.group(3)

            # Jika gateway mengandung '%', ambil hanya bagian sebelum '%'
            gateway = gateway.split("%")[0] if "%" in gateway else gateway

            data.append({
                "Flags": flags,  # Bisa DAC, AS, dll.
                "Destination": dst_address,  
                "Gateway": gateway  
            })

    # Debug: Cek hasil parsing
    print("Parsed Routes:", data)

    df = pd.DataFrame(data, columns=["Flags", "Destination", "Gateway"])

    if df.empty:
        st.warning("❗ Tidak ada route yang ditemukan.")

    return df

DNS_OPTIONS = {
    "Google DNS": ["8.8.8.8", "8.8.4.4"],
    "Cloudflare DNS": ["1.1.1.1", "1.0.0.1"],
    "OpenDNS": ["208.67.222.222", "208.67.220.220"],
    "Custom": []
}

# Halaman konfigurasi dasar
def basic_page():
    st.markdown('<div class="title">Mikrotik Basic Config Dashboard</div>', unsafe_allow_html=True)
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

    # Pastikan user sudah login
    if "ip" not in st.session_state:
        st.error("Anda belum login! Silakan login terlebih dahulu.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["🌐 IP Address", "🔍 DNS", "📃 Route List"])

    # TAB 1 - IP Configuration
    with tab1:
        st.markdown('<div class="subheader">🌐 IP Address Configuration</div>', unsafe_allow_html=True)
        ether_list = get_active_interfaces()

        if not ether_list:
            st.warning("⚠️ Tidak ada interface yang aktif.")
        else:
            # Pilih interface
            selected_interface = st.selectbox("Pilih Interface:", ether_list, key="selected_interface")

            # RESET DHCP jika ganti interface
            if "prev_selected_interface" not in st.session_state or st.session_state.prev_selected_interface != selected_interface:
                st.session_state.dhcp_attempted = False
                st.session_state.dhcp_status = None
                st.session_state.prev_selected_interface = selected_interface

            # Tombol Connect DHCP
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🔌Connect"):
                    add_dhcp_client(selected_interface)
                    st.session_state.dhcp_attempted = True
                    st.session_state.dhcp_interface = selected_interface  
                    st.session_state.dhcp_status = f"✅ DHCP Client ditambahkan ke {selected_interface}, coba periksa koneksi!"
                    st.rerun()

            # Cek status DHCP
            if st.session_state.get("dhcp_attempted"):
                dhcp_ip = get_dhcp_client_ip(st.session_state.selected_interface)

                if dhcp_ip:
                    st.session_state.dhcp_status = f"✅ DHCP Client aktif di {st.session_state.selected_interface}. IP: {dhcp_ip} (Otomatis)"
                else:
                    st.session_state.dhcp_status = f"❌ DHCP gagal di {st.session_state.selected_interface}, silakan gunakan IP Statis."

            # Tampilkan status DHCP
            if st.session_state.get("dhcp_status"):
                if "❌" in st.session_state.dhcp_status:
                    st.warning(st.session_state.dhcp_status)
                else:
                    st.success(st.session_state.dhcp_status)

            # Jika DHCP gagal, baru munculkan form IP Statis
            if st.session_state.get("dhcp_status") and "❌" in st.session_state.dhcp_status:
                st.markdown("<hr style='border: 1px solid #1A120B; margin: 20px 0;'>", unsafe_allow_html=True)
                st.markdown('<div class="subheader">🌐 IP Address Configuration</div>', unsafe_allow_html=True)

                # Mode Edit
                if "editing" in st.session_state and st.session_state.editing is not None:
                    ip_address = st.text_input("Masukkan IP Address:", value=st.session_state.edit_ip, key="edit_ip")
                    network = st.text_input("Masukkan Network:", value=st.session_state.edit_network, key="edit_network")
                    selected_ether = st.selectbox("Pilih Interface:", ether_list, index=ether_list.index(st.session_state.edit_interface), key="edit_interface")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Perbarui"):
                            command = f"/ip address set numbers={st.session_state.editing} address={ip_address} network={network} interface={selected_ether}"
                            execute_mikrotik_command(command)
                            st.session_state.editing = None  # Reset mode edit
                            st.rerun()

                    with col2:
                        if st.button("❌ Batal"):
                            st.session_state.editing = None
                            st.session_state.pop("edit_ip", None)
                            st.session_state.pop("edit_network", None)
                            st.session_state.pop("edit_interface", None)
                            st.rerun()

                # Mode Tambah Baru (Kalau DHCP gagal)
                else:
                    ip_address = st.text_input("Masukkan IP Address:", placeholder="192.168.88.1/24", key="new_ip")
                    network = st.text_input("Masukkan Network:", placeholder="192.168.88.0", key="new_network")
                    default_interface = st.session_state.get("dhcp_interface", ether_list[0])
                    selected_ether = st.selectbox("Pilih Interface:", ether_list, index=ether_list.index(default_interface), key="new_interface")

                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("➕ Set IP Statis"):
                            if not ip_address or not network or not selected_ether:
                                st.error("⚠️ Harap isi semua kolom IP Address!")
                            else:
                                command = f"/ip address add address={ip_address} network={network} interface={selected_ether}"
                                execute_mikrotik_command(command)
                                st.session_state.static_ip_used = True
                                st.rerun()

        # Garis pemisah sebelum daftar IP Address
        st.markdown("<hr style='border: 1px solid #1A120B; margin: 20px 0;'>", unsafe_allow_html=True)

        # Tabel daftar IP Address
        st.markdown('<div class="subheader" style="text-align: center;">📋 Daftar IP Address</div>', unsafe_allow_html=True)
        ip_table = fetch_ip_addresses()

        if not ip_table.empty:
            col1, col2, col3, col4, col5 = st.columns([1, 4, 3, 3, 3])
            col1.markdown("**Num**")
            col2.markdown("**IP Address**")
            col3.markdown("**Network**")
            col4.markdown("**Interface**")
            col5.markdown("**Action**")

            for index, row in ip_table.iterrows():
                col1, col2, col3, col4, col5 = st.columns([1, 4, 3, 3, 3])

                col1.write(row["Number"])
                col2.write(row["IP Address"])
                col3.write(row["Network"])
                col4.write(row["Interface"])

                with col5:
                    btn1, btn2 = st.columns([1, 1])
                    with btn1:
                        edit_btn = st.button("✏️", key=f"edit_btn_{index}_{row['IP Address']}")
                    with btn2:
                        delete_btn = st.button("🗑️", key=f"delete_btn_{index}_{row['IP Address']}")

                if edit_btn:
                    st.session_state.editing = row["Number"]
                    st.session_state.edit_ip = row["IP Address"]
                    st.session_state.edit_network = row["Network"]
                    st.session_state.edit_interface = row["Interface"]
                    st.rerun()

                if delete_btn:
                    command = f"/ip address remove numbers={row['Number']}"
                    execute_mikrotik_command(command)
                    st.rerun()

        else:
            st.warning("Tidak ada IP Address yang terdaftar.")

    with tab2:
            st.markdown('<div class="subheader">🔍 DNS Configuration</div>', unsafe_allow_html=True)
            dns_choice = st.selectbox("Pilih DNS:", list(DNS_OPTIONS.keys()))

            if dns_choice == "Custom":
                primary_dns = st.text_input("Primary DNS", placeholder="Masukkan Primary DNS")
                secondary_dns = st.text_input("Secondary DNS", placeholder="Masukkan Secondary DNS")

                col1, col2 = st.columns([4, 1])  # 5 bagian kiri, 1 bagian kanan
                with col2:
                    if st.button("➕Set DNS"):
                        if primary_dns and secondary_dns:
                            command = f"/ip dns set servers={primary_dns},{secondary_dns}"
                            execute_mikrotik_command(command)
                            st.success(f"DNS diatur ke {primary_dns}, {secondary_dns}")
                        else:
                            st.error("⚠️ Masukkan Primary & Secondary DNS!")

            else:
                # Jika bukan Custom, langsung set otomatis
                primary_dns, secondary_dns = DNS_OPTIONS[dns_choice]
                command = f"/ip dns set servers={primary_dns},{secondary_dns}"
                execute_mikrotik_command(command)
                st.success(f"DNS otomatis diatur ke {primary_dns}, {secondary_dns}")

    with tab3:
        st.markdown('<div class="subheader">📃 Route List Configuration</div>', unsafe_allow_html=True)

        # Cek apakah user menggunakan IP Statis
        if "static_ip_used" not in st.session_state:
            st.info("Route List tidak tersedia karena menggunakan DHCP.")
        else:
            # Form tambah/edit route
            dst_address = st.text_input("Masukkan Destination Address", 
                                        value=st.session_state.get("edit_dst", ""), 
                                        placeholder="0.0.0.0/0", key="dst_input")
            gateway = st.text_input("Masukkan Gateway", 
                                    value=st.session_state.get("edit_gateway", ""), 
                                    placeholder="192.168.88.1", key="gw_input")

            # Layout untuk tombol
            col1, col2, col3 = st.columns([2, 1, 1])  # Biar sejajar

            # Tombol "Set Route" di kanan
            with col3:
                if st.session_state.get("editing_route") is None:
                    if st.button("➕ Set Route"):
                        if not dst_address or not gateway:
                            st.error("⚠️ Harap isi Destination Address dan Gateway!")
                        else:
                            command = f"/ip route add dst-address={dst_address} gateway={gateway}"
                            execute_mikrotik_command(command)
                            st.success(f"Route ke {dst_address} via {gateway} berhasil ditambahkan!")
                            st.rerun()

            # Jika sedang dalam mode edit, tombol "Simpan" dan "Batal Edit" muncul
            if st.session_state.get("editing_route") is not None:
                with col1:
                    if st.button("✅ Simpan"):
                        command = f"/ip route set numbers={st.session_state.editing_route} dst-address={dst_address} gateway={gateway}"
                        execute_mikrotik_command(command)
                        st.success(f"Route ke {dst_address} via {gateway} berhasil diperbarui!")
                        st.session_state.editing_route = None
                        st.session_state.edit_dst = ""
                        st.session_state.edit_gateway = ""
                        st.rerun()

                with col3:
                    if st.button("❌ Batal"):
                        st.session_state.editing_route = None
                        st.session_state.edit_dst = ""
                        st.session_state.edit_gateway = ""
                        st.rerun()

            # Garis pemisah sebelum daftar route
            st.markdown("<hr style='border: 1px solid #1A120B; margin: 20px 0;'>", unsafe_allow_html=True)

            # Tampilkan daftar Route List
            st.markdown('<div class="subheader" style="text-align: center;">📋 Daftar Route List</div>', unsafe_allow_html=True)
            route_table = fetch_routes()

            if not route_table.empty:
                col1, col2, col3, col4 = st.columns([2, 4, 4, 3])
                col1.markdown("**Status**")
                col2.markdown("**Destination**")
                col3.markdown("**Gateway**")
                col4.markdown("**Action**")

                for index, row in route_table.iterrows():
                    col1, col2, col3, col4 = st.columns([2, 4, 4, 3])

                    col1.write(row["Flags"])
                    col2.write(row["Destination"])
                    col3.write(row["Gateway"])

                    with col4:
                        btn1, btn2 = st.columns([1, 1])
                        with btn1:
                            edit_btn = st.button("✏️", key=f"edit_btn_{index}_{row['Destination']}")
                        with btn2:
                            delete_btn = st.button("🗑️", key=f"delete_btn_{index}_{row['Destination']}")

                    if edit_btn:
                        st.session_state.editing_route = index
                        st.session_state.edit_dst = row["Destination"]
                        st.session_state.edit_gateway = row["Gateway"]
                        st.rerun()

                    if delete_btn:
                        command = f"/ip route remove numbers={index}"
                        execute_mikrotik_command(command)
                        st.success(f"Route ke {row['Destination']} berhasil dihapus!")
                        st.rerun()
            else:
                st.warning("Tidak ada route yang terdaftar.")


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


# Jalankan halaman konfigurasi
if __name__ == "__main__":
    basic_page()
