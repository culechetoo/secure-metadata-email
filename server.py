import meta
from client import Client


class Server:

    def __init__(self, domain, header_key=None, privacy_mode="pretzel"):
        self.domain = domain

        self.header_key = header_key
        self.privacy_mode = privacy_mode

        meta.domain_server_map[domain] = self

        self.users = {}

    def upgrade_privacy(self, header_key):
        self.privacy_mode = "pretzel_plus"
        self.header_key = header_key

    def add_user(self, username, domain, key):
        user = Client(username, domain, key, self)
        self.users[username] = user
        return user

    def request_client_key(self, client_username):
        client = self.users[client_username]
        return client.send_client_key()

    def request_receiver_key(self, rcvr_address):
        receiving_domain = rcvr_address.split("@")[1]
        rcvr_server = meta.domain_server_map[receiving_domain]

        return rcvr_server.request_client_key(rcvr_address.split("@")[0])

    def send(self, email):
        if self.privacy_mode == "pretzel_plus":
            receiving_domain = email["rcvr_domain"]
        else:
            receiving_domain = email["rcvr"].split("@")[1]

        rcvr_server = meta.domain_server_map[receiving_domain]

        print("Email Sent to Receiving Client")
        rcvr_server.rcv(email)

    def rcv(self, email):
        if self.privacy_mode == "pretzel":
            receiving_user = email["rcvr"].split("@")[0]

        print("Email Sent to Receiver")
        self.users[receiving_user].rcv_email(email)
