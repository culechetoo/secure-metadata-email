import time
import email
from http import client
from tracemalloc import start
import crypto
from client import Client
import socket
import pickle
import constants
import globals

MAX_QUEUE = 5


class Server:

    def __init__(self, domain, host, port, privacy_mode=constants.PRETZEL):
        self.domain = domain
        self.privacy_mode = privacy_mode

        self.host = host
        self.port = port

        self.users = {}
        self.anon_keys = []
        self.client_keys = []
        self.id_key_user_map = []

    def start_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen((MAX_QUEUE))

    def add_id_key_user_map(self, id_key, user):
        self.id_key_user_map.append({
            constants.KeyMapFields.KEY: crypto.serialize_public_key(id_key),
            constants.KeyMapFields.NAME: user
        })

    def get_user_by_id_key(self, id_key):
        for item in self.id_key_user_map:
            if item[constants.KeyMapFields.KEY] == crypto.serialize_public_key(id_key):
                return item[constants.KeyMapFields.NAME]

    def add_anon_key(self, id_key, sym_key):
        id_key_bytes = crypto.get_serialized_key(
            constants.KeyMapValues.PUBLIC_KEY, id_key)
        self.anon_keys.append({
            constants.KeyMapFields.NAME: id_key_bytes,
            constants.KeyMapFields.KEY: sym_key,
        })

    def get_anon_key_entry(self, id_key):
        id_key_bytes = crypto.get_serialized_key(
            constants.KeyMapValues.PUBLIC_KEY, id_key
        )
        for item in self.anon_keys:
            if item[constants.KeyMapFields.NAME] == id_key_bytes:
                return item

    def set_privacy_mode(self, privacy_mode):
        self.privacy_mode = privacy_mode

    def add_user(self, username, domain, host, port):
        user = Client(username, domain, self, host, port)
        self.users[username] = user
        return user

    def add_client_key(self, username, key):
        self.client_keys.append({
            constants.KeyMapFields.NAME: username,
            constants.KeyMapFields.KEY: key,
        })

    def remove_client_key(self, key):
        del_index = -1
        for i in range(len(self.client_keys)):
            entry = self.client_keys[i]
            if entry[constants.KeyMapFields.KEY] == key:
                del_index = i
                break
        if (del_index >= 0):
            del self.client_keys[del_index]

    def get_username_by_key(self, key):
        for entry in self.client_keys:
            if entry[constants.KeyMapFields.KEY] == key:
                return entry[constants.KeyMapFields.NAME]

    def send(self, email):
        receiving_domain = email["rcvr_domain"]
        rcvr_server = globals.DOMAIN_SERVER_MAP[receiving_domain]
        rcvr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rcvr_socket.connect((rcvr_server.host, rcvr_server.port))
        rcvr_socket.sendall(pickle.dumps(email, -1))
        rcvr_socket.close()

    def send_to_server(self, domain, msg, protocol, google):
        # print("Sending", msg, "to", domain, "server from", self.domain)
        server = globals.DOMAIN_SERVER_MAP[domain]
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.connect((server.host, server.port))
        data = pickle.dumps(msg, -1)
        skt.sendall(data)
        skt.close()
        globals.SERVER_BYTES_SENT += len(data)

        if protocol > 0:
            if google:
                globals.PROTOCOL_WISE_BYTES_STATS[protocol]["GOOGL_BYTES_SENT"] += len(data)
            else:
                globals.PROTOCOL_WISE_BYTES_STATS[protocol]["YAHOO_BYTES_SENT"] += len(data)

    def send_to_user(self, username, msg, protocol, google):
        # print("Sending", msg, "to", username, "user from", self.domain)
        user = self.users[username]
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.connect((user.host, user.port))
        data = pickle.dumps(msg, -1)
        skt.sendall(data)
        skt.close()
        globals.SERVER_BYTES_SENT += len(data)

        if protocol > 0:
            if google:
                globals.PROTOCOL_WISE_BYTES_STATS[protocol]["GOOGL_BYTES_SENT"] += len(data)
            else:
                globals.PROTOCOL_WISE_BYTES_STATS[protocol]["YAHOO_BYTES_SENT"] += len(data)

    def forward_email_to_server(self, email):
        domain = email[constants.EmailFields.DOMAIN]
        email[constants.MessageFields.TYPE] = constants.MessageType.EMAIL_RCV

        self.send_to_server(domain, email, 3, True)

    def forward_email_to_user(self, email):
        receiver_email = email[constants.EmailFields.RECEIVER_EMAIL]

        if self.privacy_mode == constants.PRETZEL_PLUS:
            id_key = crypto.deserialize_public_key(
                email[constants.MessageFields.ID_KEY]
            )
            symkey = self.get_anon_key_entry(
                id_key)[constants.KeyMapFields.KEY]
            receiver_email = crypto.decrypt_message_symmetric(
                *email[constants.EmailFields.RECEIVER_EMAIL], symkey
            ).decode('utf-8')

        self.send_to_user(receiver_email.split('@')[0], email, 4, False)

    def forward_server_keygen(self, msg):
        domain = msg[constants.MessageFields.DOMAIN]
        self.add_client_key(
            msg[constants.MessageFields.USERNAME], msg[constants.MessageFields.KEY]
        )
        msg[constants.MessageFields.TYPE] = constants.MessageType.SERVER_KEYGEN_RCV
        msg[constants.MessageFields.RETURN_DOMAIN] = self.domain
        del msg[constants.MessageFields.USERNAME]  # to ensure privacy
        self.send_to_server(domain, msg, 1, True)

    def forward_client_keygen_to_server(self, msg):
        domain = msg[constants.MessageFields.DOMAIN]
        public_key = crypto.deserialize_public_key(
            msg[constants.MessageFields.KEY])
        self.add_id_key_user_map(
            public_key, msg[constants.MessageFields.USERNAME])
        msg[constants.MessageFields.TYPE] = constants.MessageType.CLIENT_KEYGEN_RCV
        msg[constants.MessageFields.RETURN_DOMAIN] = self.domain
        del msg[constants.MessageFields.USERNAME]  # to ensure privacy
        self.send_to_server(domain, msg, 2, True)

    def return_client_keygen_to_server(self, msg):
        domain = msg[constants.MessageFields.DOMAIN]
        msg[constants.MessageFields.TYPE] = constants.MessageType.CLIENT_KEYGEN_RETURN_RCV
        self.send_to_server(domain, msg, -1, False)

    def return_client_keygen_to_user(self, msg):
        # print(msg[constants.MessageFields.ID_KEY])
        # print(self.id_key_user_map)
        username = self.get_user_by_id_key(
            crypto.deserialize_public_key(msg[constants.MessageFields.ID_KEY])
        )
        self.send_to_user(username, msg, 2, True)

    def forward_client_keygen_to_client(self, msg):
        email_address = None
        if self.privacy_mode == constants.PRETZEL:
            email_address = msg[constants.MessageFields.RECEIVER]
        elif self.privacy_mode == constants.PRETZEL_PLUS:
            id_key = crypto.deserialize_public_key(
                msg[constants.MessageFields.ID_KEY]
            )
            symkey = self.get_anon_key_entry(
                id_key)[constants.KeyMapFields.KEY]
            email_address = crypto.decrypt_message_symmetric(
                *msg[constants.MessageFields.RECEIVER], symkey).decode('utf-8')

        username = email_address.split('@')[0]
        self.send_to_user(username, msg, 2, False)

    def key_exchange(self, msg):
        received_public_key = crypto.deserialize_public_key(
            msg[constants.MessageFields.KEY]
        )
        return_domain = msg[constants.MessageFields.RETURN_DOMAIN]

        generated_private_key = crypto.generate_dhe_private_key()

        sym_key = crypto.get_derived_shared_key(
            generated_private_key, received_public_key
        )

        self.add_anon_key(received_public_key, sym_key)

        response_key_message = {
            constants.MessageFields.TYPE: constants.MessageType.SERVER_KEYGEN_RETURN,
            constants.MessageFields.KEY: crypto.serialize_public_key(generated_private_key.public_key()),
            constants.MessageFields.ID_KEY: crypto.serialize_public_key(received_public_key),
        }
        self.send_to_server(return_domain, response_key_message, 1, False)

    def relay_key_to_client(self, msg):
        client_key = msg[constants.MessageFields.ID_KEY]
        username = self.get_username_by_key(client_key)
        self.remove_client_key(client_key)
        self.send_to_user(username, msg, 1, True)

    def rcv_socket_loop(self):
        while True:
            conn, _ = self.socket.accept()
            msg_bytes = conn.recv(1024)
            
            start_time = time.time()
            
            if not msg_bytes:
                break

            globals.SERVER_BYTES_RECD += len(msg_bytes)

            msg = pickle.loads(msg_bytes)
            msg_type = msg['type']

            if (msg_type == constants.MessageType.SERVER_KEYGEN_FWD):  # Step 1 google
                self.forward_server_keygen(msg)
                globals.PROTOCOL_WISE_BYTES_STATS[1]["GOOGL_BYTES_RECD"] += len(msg_bytes)
                globals.PROTOCOL_WISE_TIME_STATS[1]["GOOGL_TIME"] += time.time() - start_time
            elif (msg_type == constants.MessageType.SERVER_KEYGEN_RCV):  # Step 1 yahoo
                self.key_exchange(msg)
                globals.PROTOCOL_WISE_BYTES_STATS[1]["YAHOO_BYTES_RECD"] += len(msg_bytes)
                globals.PROTOCOL_WISE_TIME_STATS[1]["YAHOO_TIME"] += time.time() - start_time
            elif (msg_type == constants.MessageType.SERVER_KEYGEN_RETURN):  # Step 1 google
                self.relay_key_to_client(msg)
                globals.PROTOCOL_WISE_BYTES_STATS[1]["GOOGL_BYTES_RECD"] += len(msg_bytes)
                globals.PROTOCOL_WISE_TIME_STATS[1]["GOOGL_TIME"] += time.time() - start_time
            elif (msg_type == constants.MessageType.CLIENT_KEYGEN_FWD):  # Step 2 google
                self.forward_client_keygen_to_server(msg)
                globals.PROTOCOL_WISE_BYTES_STATS[2]["GOOGL_BYTES_RECD"] += len(msg_bytes)
                globals.PROTOCOL_WISE_TIME_STATS[2]["GOOGL_TIME"] += time.time() - start_time
            elif (msg_type == constants.MessageType.CLIENT_KEYGEN_RCV):  # Step 2 yahoo
                self.forward_client_keygen_to_client(msg)
                globals.PROTOCOL_WISE_BYTES_STATS[2]["YAHOO_BYTES_RECD"] += len(msg_bytes)
                globals.PROTOCOL_WISE_TIME_STATS[2]["YAHOO_TIME"] += time.time() - start_time
            elif (msg_type == constants.MessageType.CLIENT_KEYGEN_RETURN_FWD):
                self.return_client_keygen_to_server(msg)
            elif (msg_type == constants.MessageType.CLIENT_KEYGEN_RETURN_RCV):  # Step 2 google
                self.return_client_keygen_to_user(msg)
                globals.PROTOCOL_WISE_BYTES_STATS[2]["GOOGL_BYTES_RECD"] += len(msg_bytes)
                globals.PROTOCOL_WISE_TIME_STATS[2]["GOOGL_TIME"] += time.time() - start_time
            elif (msg_type == constants.MessageType.EMAIL_FWD):  # Step 3 google
                self.forward_email_to_server(msg)
                globals.PROTOCOL_WISE_BYTES_STATS[3]["GOOGL_BYTES_RECD"] += len(msg_bytes)
                globals.PROTOCOL_WISE_TIME_STATS[3]["GOOGL_TIME"] += time.time() - start_time
            elif (msg_type == constants.MessageType.EMAIL_RCV):  # Step 3 yahoo
                self.forward_email_to_user(msg)
                globals.PROTOCOL_WISE_BYTES_STATS[3]["YAHOO_BYTES_RECD"] += len(msg_bytes)
                globals.PROTOCOL_WISE_TIME_STATS[3]["YAHOO_TIME"] += time.time() - start_time
            else:
                print("Incorrect message type", msg_type)

            globals.SERVER_TIME += time.time() - start_time




            # print("Received msg", msg)
