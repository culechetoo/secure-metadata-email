import time
import socket
from unicodedata import name
import constants
import crypto
import pickle
import globals


class Client:

    def __init__(self, username, domain, domain_server, host, port, privacy_mode=constants.PRETZEL):
        self.username = username
        self.domain = domain
        self.domain_server = domain_server

        self.host = host
        self.port = port

        self.privacy_mode = privacy_mode
        self.keys = []
        self.emails = []

        self.server_key = None
        self.client_key = None

    def start_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen((constants.MAX_QUEUE))

    def flush_keys(self):
        self.server_key = None
        self.client_key = None

    def add_key(self, entity, entity_name, key_type, key):
        found = False

        key_bytes = crypto.get_serialized_key(key_type, key)

        for entry in self.keys:
            if (entry[constants.KeyMapFields.ENTITY] == entity and entry[constants.KeyMapFields.NAME] == entity_name):
                found = True
                entry[constants.KeyMapFields.KEYMAP][key_type] = key_bytes
                break
        if not found:
            self.keys.append({
                constants.KeyMapFields.ENTITY: entity,
                constants.KeyMapFields.NAME: entity_name,
                constants.KeyMapFields.KEYMAP: {key_type: key_bytes},
            })

    def get_key_entry(self, entity, key_type, key):
        key_bytes = crypto.get_serialized_key(key_type, key)
        for item in self.keys:
            if item[constants.KeyMapFields.ENTITY] == entity and key_type in item[constants.KeyMapFields.KEYMAP] and item[constants.KeyMapFields.KEYMAP][key_type] == key_bytes:
                return item

    def get_key(self, entity, name, key_type):
        for item in self.keys:
            if item[constants.KeyMapFields.ENTITY] == entity and \
                    item[constants.KeyMapFields.NAME] == name and \
                    key_type in item[constants.KeyMapFields.KEYMAP]:
                return crypto.get_deserialized_key(key_type, item[constants.KeyMapFields.KEYMAP][key_type])

    def set_privacy_mode(self, privacy_mode):
        self.privacy_mode = privacy_mode

    def send_email(self, message, rcvr_address):
        domain = rcvr_address.split('@')[1]
        if globals.LOGGING:
            print(f'Client %s sending email to receiver %s with message: %s' %
                  (self.username, rcvr_address, message))
        server_id_key = self.get_key(
            constants.KeyMapValues.SERVER, domain, constants.KeyMapValues.PUBLIC_KEY
        )
        email = {
            constants.MessageFields.TYPE: constants.MessageType.EMAIL_FWD,
            constants.EmailFields.MESSAGE: crypto.encrypt_message_symmetric(message, self.client_key),
            constants.EmailFields.DOMAIN: domain,
            constants.MessageFields.ID_KEY: crypto.serialize_public_key(server_id_key),
        }

        if self.privacy_mode == constants.PRETZEL:
            email[constants.EmailFields.SENDER_EMAIL] = self.username + \
                "@"+self.domain
            email[constants.EmailFields.RECEIVER_EMAIL] = rcvr_address

        elif self.privacy_mode == constants.PRETZEL_PLUS:
            email[constants.EmailFields.SENDER_EMAIL] = crypto.encrypt_message_symmetric(
                self.username+"@"+self.domain, self.client_key)
            email[constants.EmailFields.RECEIVER_EMAIL] = crypto.encrypt_message_symmetric(
                rcvr_address, self.server_key)

        self.send_to_server(self.domain, email)

    def receive_email(self, email):
        # print("keys", self.keys)
        sym_key = self.get_key(constants.KeyMapValues.USER,
                               email[constants.MessageFields.ID_KEY], constants.KeyMapValues.SYMMETRIC_KEY)

        message = crypto.decrypt_message_symmetric(
            *email[constants.EmailFields.MESSAGE], sym_key
        ).decode('utf-8')
        sender_email = email[constants.EmailFields.SENDER_EMAIL]
        if self.privacy_mode == constants.PRETZEL_PLUS:
            sender_email = crypto.decrypt_message_symmetric(
                *email[constants.EmailFields.SENDER_EMAIL], sym_key
            ).decode('utf-8')
        if globals.LOGGING:
            print(f'Client %s received an email from sender %s with message: %s' % (
                self.username, sender_email, message))

    def send_to_server(self, domain, msg):
        # print("Sending", msg, "to", domain, "server from user", self.username)
        server = globals.DOMAIN_SERVER_MAP[domain]
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.connect((server.host, server.port))
        data = pickle.dumps(msg, -1)
        skt.sendall(data)
        skt.close()
        globals.CLIENT_BYTES_SENT += len(data)

    def generate_server_key(self, domain):
        if globals.LOGGING:
            print(f'Client %s generating key for receiving server %s' %
                  (self.username, domain))
        private_key = crypto.generate_dhe_private_key()
        public_key = private_key.public_key()
        self.add_key(constants.KeyMapValues.SERVER, domain,
                     constants.KeyMapValues.PUBLIC_KEY, public_key)
        self.add_key(constants.KeyMapValues.SERVER, domain,
                     constants.KeyMapValues.PRIVATE_KEY, private_key)

        msg = {
            constants.MessageFields.TYPE: constants.MessageType.SERVER_KEYGEN_FWD,
            constants.MessageFields.KEY: crypto.serialize_public_key(public_key),
            constants.MessageFields.DOMAIN: domain,
            constants.MessageFields.USERNAME: self.username,
        }
        self.send_to_server(self.domain, msg)

    def generate_user_key(self, username):
        if globals.LOGGING:
            print(f'Client %s generating key for receiving client %s' %
                  (self.username, username))
        domain = username.split('@')[1]
        private_key = crypto.generate_dhe_private_key()
        public_key = private_key.public_key()

        self.add_key(constants.KeyMapValues.USER, username,
                     constants.KeyMapValues.PRIVATE_KEY, private_key)
        self.add_key(constants.KeyMapValues.USER, username,
                     constants.KeyMapValues.PUBLIC_KEY, public_key)

        msg = {
            constants.MessageFields.TYPE: constants.MessageType.CLIENT_KEYGEN_FWD,
            constants.MessageFields.KEY: crypto.serialize_public_key(public_key),
            constants.MessageFields.DOMAIN: domain,
            constants.MessageFields.USERNAME: self.username,
        }

        if self.privacy_mode == constants.PRETZEL:
            self.add_key(constants.KeyMapValues.SERVER, domain,
                         constants.KeyMapValues.PUBLIC_KEY, public_key)
            self.add_key(constants.KeyMapValues.SERVER, domain,
                         constants.KeyMapValues.PRIVATE_KEY, private_key)
            msg[constants.MessageFields.RECEIVER] = username
            msg[constants.MessageFields.ID_KEY] = crypto.serialize_public_key(
                public_key
            )
        elif self.privacy_mode == constants.PRETZEL_PLUS:
            server_id_key = self.get_key(
                constants.KeyMapValues.SERVER, domain, constants.KeyMapValues.PUBLIC_KEY
            )
            msg[constants.MessageFields.RECEIVER] = crypto.encrypt_message_symmetric(
                username, self.server_key
            )
            msg[constants.MessageFields.ID_KEY] = crypto.serialize_public_key(
                server_id_key
            )

        self.send_to_server(self.domain, msg)

    def store_server_key(self, msg):
        if globals.LOGGING:
            print(f'Client %s established key with server' % self.username)
        id_key = msg[constants.MessageFields.ID_KEY]

        # print("keys for user", self.username, "in domain", self.domain, ":", self.keys)

        key_entry = self.get_key_entry(
            constants.KeyMapValues.SERVER, constants.KeyMapValues.PUBLIC_KEY, crypto.deserialize_public_key(
                id_key)
        )

        public_key = crypto.deserialize_public_key(
            msg[constants.MessageFields.KEY]
        )
        private_key = crypto.get_deserialized_key(
            constants.KeyMapValues.PRIVATE_KEY,
            key_entry[constants.KeyMapFields.KEYMAP][constants.KeyMapValues.PRIVATE_KEY]
        )
        symkey = crypto.get_derived_shared_key(private_key, public_key)

        key_entry[constants.KeyMapFields.KEYMAP][constants.KeyMapValues.SYMMETRIC_KEY] = symkey

        self.server_key = symkey

    def store_client_key(self, msg):
        if globals.LOGGING:
            print(f'Client %s established key with client' % self.username)
        id_key = msg[constants.MessageFields.ID_KEY]

        # print("keys for user", self.username, "in domain", self.domain, ":", self.keys)

        key_entry = self.get_key_entry(
            constants.KeyMapValues.USER, constants.KeyMapValues.PUBLIC_KEY, crypto.deserialize_public_key(
                id_key)
        )

        public_key = crypto.deserialize_public_key(
            msg[constants.MessageFields.KEY]
        )
        private_key = crypto.get_deserialized_key(
            constants.KeyMapValues.PRIVATE_KEY,
            key_entry[constants.KeyMapFields.KEYMAP][constants.KeyMapValues.PRIVATE_KEY]
        )
        symkey = crypto.get_derived_shared_key(private_key, public_key)

        key_entry[constants.KeyMapFields.KEYMAP][constants.KeyMapValues.SYMMETRIC_KEY] = symkey

        self.client_key = symkey

    def exchange_user_key(self, msg):
        private_key = crypto.generate_dhe_private_key()
        id_key = crypto.deserialize_public_key(
            msg[constants.MessageFields.ID_KEY])
        return_domain = msg[constants.MessageFields.RETURN_DOMAIN]
        received_public_key = crypto.deserialize_public_key(
            msg[constants.MessageFields.KEY])

        self.add_key(
            constants.KeyMapValues.USER,
            crypto.get_serialized_key(
                constants.KeyMapValues.PUBLIC_KEY, id_key
            ),
            constants.KeyMapValues.PRIVATE_KEY,
            private_key,
        )
        self.add_key(
            constants.KeyMapValues.USER,
            crypto.get_serialized_key(
                constants.KeyMapValues.PUBLIC_KEY, id_key
            ),
            constants.KeyMapValues.PUBLIC_KEY,
            private_key.public_key(),
        )

        symkey = crypto.get_derived_shared_key(
            private_key, received_public_key)
        self.add_key(
            constants.KeyMapValues.USER,
            crypto.get_serialized_key(
                constants.KeyMapValues.PUBLIC_KEY, id_key
            ),
            constants.KeyMapValues.SYMMETRIC_KEY,
            symkey,
        )

        msg = {
            constants.MessageFields.TYPE: constants.MessageType.CLIENT_KEYGEN_RETURN_FWD,
            constants.MessageFields.KEY: crypto.get_serialized_key(
                constants.KeyMapValues.PUBLIC_KEY, private_key.public_key()
            ),
            constants.MessageFields.ID_KEY: crypto.serialize_public_key(received_public_key),
            constants.MessageFields.DOMAIN: return_domain,
        }

        self.send_to_server(self.domain, msg)

    def rcv_socket_loop(self):
        while True:
            conn, _ = self.socket.accept()
            msg_bytes = conn.recv(1024)

            start_time = time.time()

            if not msg_bytes:
                break
            globals.CLIENT_BYTES_RECD += len(msg_bytes)

            msg = pickle.loads(msg_bytes)
            msg_type = msg[constants.MessageFields.TYPE]

            if (msg_type == constants.MessageType.SERVER_KEYGEN_RETURN):
                self.store_server_key(msg)
            elif (msg_type == constants.MessageType.CLIENT_KEYGEN_RCV):
                self.exchange_user_key(msg)
            elif (msg_type == constants.MessageType.CLIENT_KEYGEN_RETURN_RCV):
                self.store_client_key(msg)
            elif (msg_type == constants.MessageType.EMAIL_RCV):
                self.receive_email(msg)
            else:
                print("Incorrect message type", msg_type)

            globals.CLIENT_TIME += time.time() - start_time
