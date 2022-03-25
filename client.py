import crypto


class Client:

    def __init__(self, username, domain, message_key_path, domain_server, header_key=None, privacy_mode="pretzel"):
        self.username = username
        self.domain = domain
        self.message_key_path = message_key_path
        self.domain_server = domain_server

        self.header_key = header_key
        self.privacy_mode = privacy_mode

        self.key_cache = {}

    def upgrade_privacy(self, header_key):
        self.header_key = header_key
        self.privacy_mode = "pretzel_plus"

    def get_receiver_key(self, rcvr_address):
        if rcvr_address in self.key_cache:
            encryption_key = self.key_cache[rcvr_address]
        else:
            encryption_key = self.domain_server.request_receiver_key(rcvr_address)
            self.key_cache[rcvr_address] = encryption_key

        return encryption_key

    def send_email(self, message, rcvr_address):

        if self.privacy_mode == "pretzel":
            encryption_key = self.get_receiver_key(rcvr_address)

            email = {"message": crypto.encrypt_message(message, encryption_key),
                     "sender": self.username+"@"+self.domain, "rcvr": rcvr_address}

        else:
            # email = {"message": message, "sender_domain": self.domain,
            #          "rcvr_domain": rcvr_address.split("@")[1], }
            pass

        print("Email Sent to Sending Client")
        self.domain_server.send(email)

    def rcv_email(self, email):

        # if not self.privacy_mode:
        #     pass

        key = crypto.get_key(self.message_key_path)
        message = crypto.decrypt_message(email["message"], key)

        print("Email Received")

    def send_client_key(self):
        return crypto.get_public_key(self.message_key_path)



