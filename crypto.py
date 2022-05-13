import string
import random
import constants

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def generate_dhe_private_key():
    return ec.generate_private_key(
        ec.SECP384R1()
    )


def serialize_public_key(pub_key):
    return pub_key.public_bytes(encoding=serialization.Encoding.PEM,
                                format=serialization.PublicFormat.SubjectPublicKeyInfo)


def serialize_private_key(private_key):
    return private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                     format=serialization.PrivateFormat.PKCS8,
                                     encryption_algorithm=serialization.BestAvailableEncryption(b'password'))


def get_serialized_key(key_type, key):
    key_bytes = key
    if (key_type == constants.KeyMapValues.PUBLIC_KEY):
        key_bytes = serialize_public_key(key)
    elif (key_type == constants.KeyMapValues.PRIVATE_KEY):
        key_bytes = serialize_private_key(key)

    return key_bytes


def get_deserialized_key(key_type, bytes):
    transformed_key = bytes
    if (key_type == constants.KeyMapValues.PUBLIC_KEY):
        transformed_key = deserialize_public_key(bytes)
    elif (key_type == constants.KeyMapValues.PRIVATE_KEY):
        transformed_key = deserialize_private_key(bytes)

    return transformed_key


def deserialize_public_key(bytes):
    return serialization.load_pem_public_key(bytes)


def deserialize_private_key(bytes):
    return serialization.load_pem_private_key(bytes, password=b'password')


def get_derived_shared_key(private_key, peer_public_key):
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(shared_key)

    return derived_key


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
        print("Key incorrect or message corrupted", "key=", key, "ciphertext=", ciphertext)


def generate_asymmetric():
    key = RSA.generate(2048)
    return key


def generate_symmetric():
    key_phrase = ("".join(random.choice(string.ascii_lowercase)
                  for _ in range(16))).encode("utf-8")
    return key_phrase


def get_key(message_key_path):
    key = RSA.import_key(open(message_key_path).read())
    return key


def get_public_key(message_key_path):
    key = RSA.import_key(open(message_key_path).read())
    return key.public_key()
