import crypto


class Client:

    def __init__(self, username, domain, message_key_path, domain_server, privacy_mode="pretzel"):
        self.username = username
        self.domain = domain
        self.message_key_path = message_key_path
        self.domain_server = domain_server

        self.privacy_mode = privacy_mode

        self.key_cache = {}

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

    def send_email(self, message, rcvr_address):

        email = {}

        if self.privacy_mode == "pretzel":
            encryption_key = self.get_receiver_key(rcvr_address)

            email = {"message": crypto.encrypt_message(message, encryption_key),
                     "sender": self.username+"@"+self.domain, "rcvr": rcvr_address}

        elif self.privacy_mode == "pretzel_plus":
            keys = self.get_receiver_key(rcvr_address)
            message_key = keys["message_key"]
            header_key = keys["header_key"]

            email = {"message": crypto.encrypt_message(message, message_key),
                     "sender_username": crypto.encrypt_message(self.username, message_key),
                     "rcvr_username": crypto.encrypt_message(rcvr_address.split("@")[0], header_key),
                     "sender_domain": self.domain, "rcvr_domain": rcvr_address.split("@")[1]}

        self.domain_server.send(email)

    def rcv_email(self, email):

        key = crypto.get_key(self.message_key_path)

        if self.privacy_mode == "pretzel_plus":
            sender = crypto.decrypt_message(email["sender_username"], key)
        message = crypto.decrypt_message(email["message"], key)


    def send_client_key(self):
        return crypto.get_public_key(self.message_key_path)



