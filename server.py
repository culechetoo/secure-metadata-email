import meta
import crypto
from client import Client
import socket
import pickle

MAX_QUEUE = 5

class Server:

    def __init__(self, domain, header_key_path, host, port, privacy_mode="pretzel"):
        self.domain = domain

        self.header_key_path = header_key_path
        self.privacy_mode = privacy_mode

        self.host = host
        self.port = port

        meta.domain_server_map[domain] = self

        self.users = {}

    def start_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen((MAX_QUEUE))

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
            return {
                "rcvr_key": client_key,
                "server_key": crypto.get_public_key(self.header_key_path),
            }

    def request_receiver_key(self, rcvr_address):
        receiving_domain = rcvr_address.split("@")[1]
        rcvr_server = meta.domain_server_map[receiving_domain]

        return rcvr_server.request_client_key(rcvr_address.split("@")[0])

    def send(self, email):
        receiving_domain = email["rcvr_domain"]
        rcvr_server = meta.domain_server_map[receiving_domain]
        rcvr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rcvr_socket.connect((rcvr_server.host, rcvr_server.port))
        rcvr_socket.sendall(pickle.dumps(email, -1))
        rcvr_socket.close()

    def rcv(self, email):
        receiving_user = ""

        if self.privacy_mode == "pretzel":
            receiving_user = email["rcvr_username"]
        elif self.privacy_mode == "pretzel_plus":
            receiving_user = crypto.decrypt_message_asymmetric(email["rcvr_username"],
                                                               crypto.get_key(self.header_key_path)).decode("utf-8")

        self.users[receiving_user].rcv_email(email)
    
    def rcv_socket_loop(self):
        while True:
            conn, addr = self.socket.accept()
            email_bytes = conn.recv(1024)
            if not email_bytes: break
            email = pickle.loads(email_bytes)

            # print("Received email", email)

            self.rcv(email)
