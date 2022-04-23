import random
import pickle

import meta
from Crypto.PublicKey import RSA

from server import Server
import socket

host = socket.gethostname()
starting_port = 6100
domain_names = ["gmail.com", "yahoo.com", "hotmail.com", "nyu.edu", "outlook.com"]
usernames = ["chaitanya", "shantanu", "anirudh", "sriram", "pranav", "yajur", "raghav", "agarwal",
             "dahiya", "sivaraman", "ramesh", "jain", "ahuja"]

server_map = {}

for i in range(len(domain_names)):
    domain_name = domain_names[i]
    port = str(starting_port + i) # consecutive port numbers
    rsa_key = RSA.generate(2048)
    key_file = open("data/keys/"+domain_name+"_header", 'wb')
    key_file.write(rsa_key.exportKey())

    server_map[domain_name] = Server(domain_name, "data/keys/"+domain_name+"_header", host, int(port))


for username in usernames:
    domain = random.choice(domain_names)
    domain_server = meta.domain_server_map[domain]

    rsa_key = RSA.generate(2048)
    key_file = open("data/keys/"+username+"_message", 'wb')
    key_file.write(rsa_key.exportKey())

    user = domain_server.add_user(username, domain, "data/keys/"+username+"_message")

for domain_name in domain_names:
    pickle.dump(server_map[domain_name], open("data/server/"+domain_name, 'wb'))
