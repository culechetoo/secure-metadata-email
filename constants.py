import enum

PRETZEL = "pretzel"
PRETZEL_PLUS = "pretzel_plus"

MAX_QUEUE = 5


class MessageType(enum.Enum):
    SERVER_KEYGEN_RCV = 1
    SERVER_KEYGEN_FWD = 2
    SERVER_KEYGEN_RETURN = 3
    CLIENT_KEYGEN_FWD = 4
    CLIENT_KEYGEN_RCV = 5
    CLIENT_KEYGEN_RETURN_FWD = 6
    CLIENT_KEYGEN_RETURN_RCV = 7
    EMAIL_FWD = 8
    EMAIL_RCV = 9


class MessageFields:
    TYPE = "type"
    KEY = "key"
    ID_KEY = "id_key"
    DOMAIN = "domain"
    RETURN_DOMAIN = "return_domain"
    USERNAME = "username"
    RECEIVER = "receiver"


class KeyMapFields:
    KEYMAP = "keymap"
    KEY = "key"
    ENTITY = "entity"
    NAME = "name"

class KeyMapValues:
    SERVER = "server"
    USER = "user"
    PUBLIC_KEY = "public_key"
    PRIVATE_KEY = "private_key"
    SYMMETRIC_KEY = "symmetric_key"

class EmailFields:
    MESSAGE = "message"
    RECEIVER_EMAIL = "receiver_email"
    SENDER_EMAIL = "sender_email"
    DOMAIN = "domain"