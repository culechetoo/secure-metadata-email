import os
import random
import string
import pickle
import time

import meta


users = []
email_addresses = []


def generate_random_email():
    mess_length = random.randint(0, 200)
    message = "".join(random.choice(string.ascii_lowercase) for _ in range(mess_length))
    return message, random.choice(email_addresses)


def read_data():
    for server_file in os.listdir("data/server"):
        server = pickle.load(open("data/server/"+server_file, 'rb'))
        meta.domain_server_map[server.domain] = server
        for username, user in server.users.items():
            users.append(user)
            email_addresses.append(username+"@"+server.domain)


read_data()
emails = []

start_time = time.time()

# for i in range(1000):
#     print("Sending email", i+1)
#     message, rcvr_email = generate_random_email()
#     emails.append((message, rcvr_email))
#     sender = random.choice(users)
#
#     sender.send_email(message, rcvr_email)
#
# print(f"Time taken for pretzel: %.4f seconds" % (time.time()-start_time))

for domain, server in meta.domain_server_map.items():
    server.set_privacy_mode("pretzel_plus")

for user in users:
    user.set_privacy_mode("pretzel_plus")

start_time = time.time()

for i in range(100):
    print("Sending email", i+1)
    message, rcvr_email = generate_random_email()
    sender = random.choice(users)

    sender.send_email(message, rcvr_email)

print(f"Time taken for pretzel plus: %.4f seconds" % (time.time()-start_time))
