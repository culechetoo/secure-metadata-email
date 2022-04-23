import string
import random

import crypto


class Client:

    def __init__(self, username, domain, message_key_path, domain_server, privacy_mode="pretzel"):
        self.username = username
        self.domain = domain
        self.message_key_path = message_key_path
        self.domain_server = domain_server

        self.privacy_mode = privacy_mode

        self.key_cache = {}
        self.symmetric_key_cache = {}

    def set_privacy_mode(self, privacy_mode):
        self.privacy_mode = privacy_mode
        self.key_cache = {}

    def get_receiver_key(self, rcvr_address):
        if rcvr_address in self.key_cache:
            encryption_key = self.key_cache[rcvr_address]
        else:
            encryption_key = self.domain_server.request_receiver_key(rcvr_address)
            self.key_cache[rcvr_address] = encryption_key

        return encryption_key

    def generate_symmetric_key(self, rcvr_address):
        if rcvr_address in self.symmetric_key_cache:
            return self.symmetric_key_cache[rcvr_address]
        else:
            key = crypto.generate_symmetric()
            self.symmetric_key_cache[rcvr_address] = key
            return key

    def send_email(self, message, rcvr_address):

        email = {}

        if self.privacy_mode == "pretzel":
            encryption_key = self.get_receiver_key(rcvr_address)

            email = {
                "message": crypto.encrypt_message_asymmetric(message, encryption_key),
                "sender": self.username+"@"+self.domain, 
                "rcvr_username": rcvr_address.split("@")[0],
                "rcvr_domain": rcvr_address.split("@")[1],
            }

        elif self.privacy_mode == "pretzel_plus":
            keys = self.get_receiver_key(rcvr_address)
            receiver_key = keys["rcvr_key"]
            server_key = keys["server_key"]

            receiver_sym_key = self.generate_symmetric_key(rcvr_address)

            encrypted_message = crypto.encrypt_message_symmetric(message, receiver_sym_key)
            encrypted_sender_username = crypto.encrypt_message_symmetric(self.username, receiver_sym_key)

            encrypted_receiver_sym_key = crypto.encrypt_message_asymmetric(receiver_sym_key, receiver_key)

            email = {
                "message": encrypted_message,
                "sender_username": encrypted_sender_username,
                "sender_domain": self.domain, 
                "rcvr_username": crypto.encrypt_message_asymmetric(rcvr_address.split("@")[0], server_key),
                "rcvr_domain": rcvr_address.split("@")[1],
                "encrypted_rcvr_sym_key": encrypted_receiver_sym_key,
            }

        self.domain_server.send(email)

    def rcv_email(self, email):

        key = crypto.get_key(self.message_key_path)
        if self.privacy_mode == "pretzel":
            message = crypto.decrypt_message_asymmetric(email["message"], key)

        elif self.privacy_mode == "pretzel_plus":
            receiver_sym_key = crypto.decrypt_message_asymmetric(email["encrypted_rcvr_sym_key"], key)

            message = crypto.decrypt_message_symmetric(*email["message"], receiver_sym_key)
            sender_username = crypto.decrypt_message_symmetric(*email["sender_username"], receiver_sym_key)

    def send_client_key(self):
        return crypto.get_public_key(self.message_key_path)
