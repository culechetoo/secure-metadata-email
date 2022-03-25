import string
import random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES


def encrypt_message_asymmetric(message, key):
    cipher = PKCS1_OAEP.new(key)
    if type(message) is bytes:
        return cipher.encrypt(message)
    else:
        return cipher.encrypt(message.encode("utf-8"))


def decrypt_message_asymmetric(ciphertext, key):
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(ciphertext)


def encrypt_message_symmetric(message, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message.encode("utf-8"))

    return nonce, ciphertext, tag


def decrypt_message_symmetric(nonce, ciphertext, tag, key):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext
    except ValueError:
        print("Key incorrect or message corrupted")


def generate_asymmetric():
    key = RSA.generate(2048)
    return key


def generate_symmetric():
    key_phrase = ("".join(random.choice(string.ascii_lowercase) for _ in range(16))).encode("utf-8")
    return key_phrase


def get_key(message_key_path):
    key = RSA.import_key(open(message_key_path).read())
    return key


def get_public_key(message_key_path):
    key = RSA.import_key(open(message_key_path).read())
    return key.public_key()