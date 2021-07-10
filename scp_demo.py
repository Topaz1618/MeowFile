__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'


import paramiko
from scp import SCPClient

from config import INTRANET_HOST, EXTERNAL_HOST
from config import SSH_PORT, EXTERNAL_SSH_USERNAME, EXTERNAL_SSH_PWD , INTRANET_SSH_USERNAME , INTRANET_SSH_PWD


def get_from_remote(filename, host):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    if host == INTRANET_HOST:
        # remote_path = "Desktop/user.txt"
        remote_path = "Desktop/managefile/download"
        ssh_client.connect(host, SSH_PORT, "Administrator", "1234qwer")
    else:
        remote_path = "/home/dms/"
        ssh_client.connect(host, SSH_PORT, EXTERNAL_SSH_USERNAME, EXTERNAL_SSH_PWD)

    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)

    try:
        scpclient.get(remote_path, "download/")
    except FileNotFoundError as e:
        print(e)
        print(f"File does not exist: {filename}")
    else:
        print(f"Get file [{filename}] successful!")
    ssh_client.close()


def put_to_remote_win(filename, host):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    remote_path = f"Desktop/managefile/download/"
    ssh_client.connect(host, SSH_PORT, "Administrator", "1234qwer")
    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)

    try:
        scpclient.put(filename, remote_path)

    except FileNotFoundError as e:
        print(e)
        print(f"File does not exist: {filename}")
    else:
        print(f"Put [{filename}] successful!")
    ssh_client.close()


def put_to_remote(filename, host):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    remote_path = "/home/dms/"
    print(">>>", host, INTRANET_SSH_USERNAME, INTRANET_SSH_PWD)
    ssh_client.connect(host, 22, "dms", "12dms")

    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)

    try:
        scpclient.put(filename, remote_path)
    except FileNotFoundError as e:
        print(e)
        print(f"File does not exist: {filename}")
    else:
        print(f"Get file [{filename}] successful!")
    ssh_client.close()


if __name__ == "__main__":
    host = "192.168.0.210"
    put_to_remote("download/《夺冠》.mp4", host)
