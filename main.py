import os
import random
import string
import pickle

import meta


users = []
emails = []


def generate_random_email():
    mess_length = random.randint(0, 200)
    message = "".join(random.choice(string.ascii_lowercase) for _ in range(mess_length))
    return message, random.choice(emails)


def read_data():
    for server_file in os.listdir("data/server"):
        server = pickle.load(open("data/server/"+server_file, 'rb'))
        meta.domain_server_map[server.domain] = server
        for username, user in server.users.items():
            users.append(user)
            emails.append(username+"@"+server.domain)


read_data()


for i in range(100):
    message, rcvr_email = generate_random_email()
    sender = random.choice(users)

    sender.send_email(message, rcvr_email)

