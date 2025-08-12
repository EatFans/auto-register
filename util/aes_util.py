import base64,hashlib,os
from Crypto.Cipher import AES


def openssl_key_iv_gen(password, salt, key_len, iv_len):
    """等效于 OpenSSL EVP_BytesToKey"""
    dt = b""
    while len(dt) < key_len + iv_len:
        prev = dt[-16:] if len(dt) >= 16 else b""
        dt += hashlib.md5(prev + password + salt).digest()
    return dt[:key_len], dt[key_len:key_len+iv_len]

def decrypt_openssl_aes(ciphertext_b64):
    """
    解密
    :param ciphertext_b64:
    :return:
    """
    password = "72580554c8182806b3e0984e7b6529ded5693935343844e2fde8025b3ab544bd"
    ct_bytes = base64.b64decode(ciphertext_b64)
    assert ct_bytes[:8] == b"Salted__"
    salt = ct_bytes[8:16]
    key, iv = openssl_key_iv_gen(password.encode(), salt, 32, 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ct_bytes[16:])
    pad_len = plaintext[-1]
    return plaintext[:-pad_len].decode()

def encrypt_openssl_aes(plaintext):
    """
    加密
    :param plaintext:
    :return:
    """
    password = "72580554c8182806b3e0984e7b6529ded5693935343844e2fde8025b3ab544bd"
    salt = os.urandom(8)
    # salt = b"12345678"  # 固定盐
    key, iv = openssl_key_iv_gen(password.encode(), salt, 32, 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # PKCS#7 填充
    pad_len = 16 - len(plaintext.encode()) % 16
    padded = plaintext.encode() + bytes([pad_len] * pad_len)
    ciphertext = cipher.encrypt(padded)
    return base64.b64encode(b"Salted__" + salt + ciphertext).decode()

if __name__ == '__main__':
    ciphertext = "U2FsdGVkX19GGb2TJgDy9kPnI97IWLuijNrz58EK67A="
    print(decrypt_openssl_aes(ciphertext))

    test = "Zijian"
    test2 = encrypt_openssl_aes(test)
    print(test2)
    print(decrypt_openssl_aes(test2))
