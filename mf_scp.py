__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import paramiko
from scp import SCPClient

from config import INTRANET_HOST, EXTERNAL_HOST
from config import SSH_PORT, EXTERNAL_SSH_USERNAME, EXTERNAL_SSH_PWD, INTRANET_SSH_USERNAME, INTRANET_SSH_PWD


def put_to_remote(filename, host):
    remote_path = "/home/dms/Project/ManageFile/download"
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    if host == INTRANET_HOST:
        ssh_client.connect(host, SSH_PORT, INTRANET_SSH_USERNAME, INTRANET_SSH_PWD)
    else:
        ssh_client.connect(host, SSH_PORT, EXTERNAL_SSH_USERNAME, EXTERNAL_SSH_PWD)

    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
    try:
        scpclient.put(filename, remote_path)
    except FileNotFoundError as e:
        print(e)
        print(f"File does not exist: {filename}")
    else:
        print(f"Put file [{filename}] successful!")
    ssh_client.close()


def get_from_remote(filename):
    try:
        remote_path = f"/home/dms/Project/ManageFile/{filename}"

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh_client.connect(INTRANET_HOST, SSH_PORT, INTRANET_SSH_USERNAME, INTRANET_SSH_PWD)
        scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)

        try:
            scpclient.get(remote_path, "download")
        except FileNotFoundError as e:
            print(e)
            print(f"File does not exist: {remote_path}")
        else:
            print(f"Scp get file [{filename}] successful! ")
        ssh_client.close()
    except Exception as e:
        print(e)


def put_to_remote_win(filename, host):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    if host == INTRANET_HOST:
        remote_path = f"Desktop/managefile/download/"
        ssh_client.connect(host, SSH_PORT, "Administrator", "1234qwer")
    else:
        remote_path = "/home/dms/"
        ssh_client.connect(host, SSH_PORT, EXTERNAL_SSH_USERNAME, EXTERNAL_SSH_PWD)

    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)

    try:
        scpclient.put(filename, remote_path)
    except FileNotFoundError as e:
        print(e)
        print(f"File does not exist: {filename}")
    else:
        print(f"Put file [{filename}] successful!")
    ssh_client.close()

# def get_from_remote_win(filename):
#     try:
#         remote_path = f"/home/dms/Project/ManageFile/{filename}"
#
#         ssh_client = paramiko.SSHClient()
#         ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
#         ssh_client.connect(INTRANET_HOST, SSH_PORT, SSH_USERNAME, SSH_PWD)
#         scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
#
#         try:
#             scpclient.get(remote_path, "download")
#         except FileNotFoundError as e:
#             print(e)
#             print(f"File does not exist: {remote_path}")
#         else:
#             print(f"Scp get file [{filename}] successful! ")
#         ssh_client.close()
#     except Exception as e:
#         print(e)


if __name__ == "__main__":
    # local_to_remote("download/a.mp4", EXTERNAL_HOST)
    # get_from_remote("download/a.mp4")
    name = "download/夺冠.mp4"
    put_to_remote_win(name, "192.168.0.111")
