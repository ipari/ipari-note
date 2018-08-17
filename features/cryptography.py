import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .config import config


PADDING = '$'
AES_KEY_LENGTH = 32


def secret_key():
    key = config('secret')['key']

    if len(key) > AES_KEY_LENGTH:
        key = key[:AES_KEY_LENGTH]

    if len(key) < AES_KEY_LENGTH:
        key += (AES_KEY_LENGTH - len(key)) * PADDING

    return key.encode()


def iv():
    return secret_key()[::2][::-1]


def encrypt(text):
    cipher = AES.new(secret_key(), AES.MODE_CBC, iv())
    encrypted = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.urlsafe_b64encode(encrypted).decode('utf-8')


def decrypt(encrypted):
    try:
        cipher = AES.new(secret_key(), AES.MODE_CBC, iv())
        encrypted = base64.urlsafe_b64decode(encrypted)
        decrypted = cipher.decrypt(encrypted)
        return unpad(decrypted, AES.block_size).decode('utf-8')
    except ValueError:
        return None
