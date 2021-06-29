import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from app.config.model import Config

PADDING = '$'
AES_KEY_LENGTH = 32


def get_aes_key():
    # FIXME: 설정에서 가져오도록
    key = Config.get('aes_key')
    if len(key) > AES_KEY_LENGTH:
        key = key[:AES_KEY_LENGTH]
    if len(key) < AES_KEY_LENGTH:
        key += (AES_KEY_LENGTH - len(key)) * PADDING
    return key.encode()


def get_secret():
    key = get_aes_key()
    iv = key[::2][::-1]
    return key, iv


def encrypt(text):
    key, iv = get_secret()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.urlsafe_b64encode(encrypted).decode('utf-8')


def decrypt(encrypted):
    if encrypted is None:
        return None

    key, iv = get_secret()
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = base64.urlsafe_b64decode(encrypted)
        decrypted = cipher.decrypt(encrypted)
        return unpad(decrypted, AES.block_size).decode('utf-8')
    except ValueError:
        return None
