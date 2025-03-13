import paramiko

def execute_mikrotik_command(host, username, password, command):
    try:
        # Membuat koneksi SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password)
        
        # Eksekusi perintah
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        client.close()
        return output if output else error
    except Exception as e:
        return str(e)
