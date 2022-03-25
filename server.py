import meta
import crypto
from client import Client


class Server:

    def __init__(self, domain, header_key_path, privacy_mode="pretzel"):
        self.domain = domain

        self.header_key_path = header_key_path
        self.privacy_mode = privacy_mode

        meta.domain_server_map[domain] = self

        self.users = {}

    def set_privacy_mode(self, privacy_mode):
        self.privacy_mode = privacy_mode

    def add_user(self, username, domain, key):
        user = Client(username, domain, key, self)
        self.users[username] = user
        return user

    def request_client_key(self, client_username):
        if self.privacy_mode == "pretzel":
            client = self.users[client_username]
            return client.send_client_key()
        elif self.privacy_mode == "pretzel_plus":
            client = self.users[client_username]
            client_key = client.send_client_key()
            return {"message_key": client_key, "header_key": crypto.get_public_key(self.header_key_path)}

    def request_receiver_key(self, rcvr_address):
        receiving_domain = rcvr_address.split("@")[1]
        rcvr_server = meta.domain_server_map[receiving_domain]

        return rcvr_server.request_client_key(rcvr_address.split("@")[0])

    def send(self, email):

        receiving_domain = ""

        if self.privacy_mode == "pretzel_plus":
            receiving_domain = email["rcvr_domain"]
        elif self.privacy_mode == "pretzel":
            receiving_domain = email["rcvr"].split("@")[1]

        rcvr_server = meta.domain_server_map[receiving_domain]

        rcvr_server.rcv(email)

    def rcv(self, email):

        receiving_user = ""

        if self.privacy_mode == "pretzel":
            receiving_user = email["rcvr"].split("@")[0]
        elif self.privacy_mode == "pretzel_plus":
            receiving_user = crypto.decrypt_message(email["rcvr_username"], crypto.get_key(self.header_key_path))

        self.users[receiving_user].rcv_email(email)
