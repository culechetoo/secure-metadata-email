import random
from server import Server
import socket
from globals import DOMAIN_SERVER_MAP

host = socket.gethostname()
starting_port = 6100

domain_names = [
    "gmail.com", 
    "yahoo.com", 
    "hotmail.com", 
    "nyu.edu", 
    "outlook.com",
]

usernames = [
    "chaitanya",
    "shantanu",
    "anirudh",
    "sriram",
    "pranav",
    "yajur",
    "raghav",
    "agarwal",
    "dahiya",
    "sivaraman",
    "ramesh",
    "jain",
    "ahuja",
]

for i in range(len(domain_names)):
    domain_name = domain_names[i]
    port = str(starting_port + i) # consecutive port numbers

    DOMAIN_SERVER_MAP[domain_name] = Server(domain_name, host, int(port))


for username in usernames:
    port = str(int(port) + 1)
    domain = random.choice(domain_names)
    domain_server = DOMAIN_SERVER_MAP[domain]

    user = domain_server.add_user(username, domain, host, int(port))
