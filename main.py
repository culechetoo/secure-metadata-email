import os
import random
from re import T
import string
import pickle
import time
import sys
import threading
import meta # create data
from globals import DOMAIN_SERVER_MAP

EMAIL_COUNT = 10

users = []
email_addresses = []

def generate_random_email():
    mess_length = random.randint(0, 200)
    message = "".join(random.choice(string.ascii_lowercase) for _ in range(mess_length))
    return message, random.choice(email_addresses)


for server in DOMAIN_SERVER_MAP.values():
    server.start_socket()
    t = threading.Thread(target=server.rcv_socket_loop)
    t.start()
    
    for username, user in server.users.items():
        user.start_socket()
        t = threading.Thread(target=user.rcv_socket_loop)
        t.start()
        users.append(user)
        email_addresses.append(username+"@"+server.domain)

emails = []

def gen_emails():
    for i in range(EMAIL_COUNT):
        if (i == EMAIL_COUNT-1):
            print(f"Generating email %d" % (i+1))
        else:
            print(f"Generating email %d" % (i+1), end='\r')
        message, rcvr_email = generate_random_email()
        emails.append((message, rcvr_email))

gen_emails()

start_time = time.time()

for i in range(EMAIL_COUNT):
    if (i == EMAIL_COUNT-1):
        print(f"Sending pretzel email %d" % (i+1))
    else:
        print(f"Sending pretzel email %d" % (i+1), end='\r')

    message, rcvr_email = emails[i]
    sender = random.choice(users)

    sender.generate_user_key(rcvr_email)
    while(not sender.client_key):
        continue
    sender.send_email(message, rcvr_email)
    sender.flush_keys()

end_time = time.time()

print(f"Time taken for pretzel: %.4f seconds" % (end_time-start_time))
print(f"Time per email for pretzel: %.4f seconds" % ((end_time-start_time)/float(EMAIL_COUNT)))

time.sleep(5) # wait for any pending operations to clear

for domain, server in DOMAIN_SERVER_MAP.items():
    server.set_privacy_mode("pretzel_plus")

for user in users:
    user.set_privacy_mode("pretzel_plus")

start_time = time.time()

for i in range(EMAIL_COUNT):
    if (i == EMAIL_COUNT-1):
        print(f"Sending pretzel plus email %d" % (i+1))
    else:
        print(f"Sending pretzel plus email %d" % (i+1), end='\r')
    message, rcvr_email = emails[i]
    sender = random.choice(users)

    sender.generate_server_key(rcvr_email.split('@')[1])
    while(not sender.server_key):
        continue
    sender.generate_user_key(rcvr_email)
    while(not sender.client_key):
        continue
    sender.send_email(message, rcvr_email)
    sender.flush_keys()

end_time = time.time()

print(f"Time taken for pretzel plus: %.4f seconds" % (end_time-start_time))
print(f"Time per email for pretzel plus: %.4f seconds" % ((end_time-start_time)/float(EMAIL_COUNT)))
