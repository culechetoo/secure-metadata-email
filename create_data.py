import random
import pickle

import meta
import crypto

from server import Server


domain_names = ["gmail.com", "yahoo.com", "hotmail.com", "nyu.edu", "outlook.com"]
usernames = ["chaitanya", "shantanu", "anirudh", "sriram", "pranav", "yajur", "raghav", "agarwal",
             "dahiya", "sivaraman", "ramesh", "jain", "ahuja"]

server_map = {}

for domain_name in domain_names:
    rsa_key = crypto.generate()
    key_file = open("data/keys/"+domain_name+"_header", 'wb')
    key_file.write(rsa_key.exportKey())

    server_map[domain_name] = Server(domain_name, "data/keys/"+domain_name+"_header")

for username in usernames:
    domain = random.choice(domain_names)
    domain_server = meta.domain_server_map[domain]

    rsa_key = crypto.generate()
    key_file = open("data/keys/"+username+"_message", 'wb')
    key_file.write(rsa_key.exportKey())

    user = domain_server.add_user(username, domain, "data/keys/"+username+"_message")

for domain_name in domain_names:
    pickle.dump(server_map[domain_name], open("data/server/"+domain_name, 'wb'))
