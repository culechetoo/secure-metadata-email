from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def encrypt_message(message, key):
    cipher = PKCS1_OAEP.new(key)
    return cipher.encrypt(message.encode("utf-8"))


def decrypt_message(ciphertext, key):
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(ciphertext)


def generate():
    key = RSA.generate(2048)
    return key


def get_key(message_key_path):
    key = RSA.import_key(open(message_key_path).read())
    return key

def get_public_key(message_key_path):
    key = RSA.import_key(open(message_key_path).read())
    return key.public_key()