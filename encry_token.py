__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

"""
    1. 加密
        Step1: generate_keypair() 生成密钥对 .
        Step2: 公钥加密 token (json 格式) 如下:
            token_dic = {
                "username": "",
                "machine_id": "",
                "timestamp": time(),
                "model_name": "man01",
            }
        Step3: DES 加密上一步得到结果 .

    2. 解密
        Step1: 私钥解密两次加密过的 token .
        Step2: DES 解密上一步结果 .
        Step3: json.loads("des_result".split("=")[0]) => Token dict .

"""

import json
import binascii
from time import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import DES
from Crypto.Cipher import PKCS1_OAEP


from config import TOKEN_KEY


def generate_keypair():
    keyPair = RSA.generate(3072)

    pubKey = keyPair.publickey()
    pubKeyPEM = pubKey.exportKey()
    public_key = pubKeyPEM.decode('ascii')
    privKeyPEM = keyPair.exportKey()
    private_key = privKeyPEM.decode('ascii')

    with open("public.pem", "w") as f:
        f.write(public_key)

    with open("private.pem", "w") as f:
        f.write(private_key)

    print("Public key ", public_key)
    print("Private key ", private_key)


def encry_rsa(msg):
    with open("public.pem", 'r') as f:
        key = f.read()
    public_key = RSA.importKey(key)
    encryptor = PKCS1_OAEP.new(public_key)
    encrypted = encryptor.encrypt(msg)
    print("Encrypted:", binascii.hexlify(encrypted))
    return encrypted


def decrypt_rsa(encrypted):
    with open("private.pem", 'r') as f:
        key = f.read()
    privite_key = RSA.importKey(key)
    decryptor = PKCS1_OAEP.new(privite_key)
    decrypted = decryptor.decrypt(encrypted)
    print('Decrypted:', decrypted)
    return decrypted


def engry_des(token):
    des = DES.new(TOKEN_KEY, DES.MODE_ECB)
    text = token + (8 - (len(token) % 8)) * '='
    hex_text = des.encrypt(text.encode())  # Hexadecimal representation of binary data
    encry_text = binascii.b2a_hex(hex_text)
    return encry_text


def decrypt_des(encry_text):
    if not isinstance(encry_text, bytes):
        encry_text = encry_text.encode()
    des = DES.new(TOKEN_KEY, DES.MODE_ECB)
    binary_text = binascii.a2b_hex(encry_text)  # Binary data of hexadecimal representation.
    decrypt_text = des.decrypt(binary_text).decode()
    return decrypt_text


if __name__ == "__main__":
    generate_keypair()

    token_dic = {
        "username": "111111",
        "machine_id": "9djdxkdkjfksda",
        "timestamp": time(),
        "model_name": "man01",
    }
    token_str = json.dumps(token_dic)

    # 加密
    encrypted_des = engry_des(token_str)
    encrypted = encry_rsa(encrypted_des)
    res_token = binascii.hexlify(encrypted).decode()
    print(res_token)

    # 解密
    encrypted = binascii.unhexlify(res_token.encode())
    decrypted = decrypt_rsa(encrypted)
    decrypted_des = decrypt_des(decrypted)
    token_str = decrypted_des.split("=")[0]
    token = json.loads(token_str)
    print(token)

