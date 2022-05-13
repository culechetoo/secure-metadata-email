import globals
import constants
import os
import random
from re import T
import string
import pickle
import time
import sys
import threading
import meta  # create data

EMAIL_COUNT = 1000

users = []
email_addresses = []

globals.reset_params()


def print_stats(privacy_mode):
    print()
    print('- - - - - S T A T S - - - - -')
    print(f"Total time for %s: %.4f seconds" %
          (privacy_mode, end_time-start_time))
    print(f"Time per email for %s: %.4f seconds" %
          (privacy_mode, (end_time-start_time)/float(EMAIL_COUNT)))
    print()


def generate_random_email():
    mess_length = random.randint(0, 200)
    message = "".join(random.choice(string.ascii_lowercase)
                      for _ in range(mess_length))
    return message, random.choice(email_addresses)


for domain, server in globals.DOMAIN_SERVER_MAP.items():
    server.set_privacy_mode(constants.PRETZEL)

for user in users:
    user.set_privacy_mode(constants.PRETZEL)

for server in globals.DOMAIN_SERVER_MAP.values():
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

print()

print('* * * * * * * * * * * * * *  P R E T Z E L  * * * * * * * * * * * * * *')

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

print_stats(constants.PRETZEL)

time.sleep(5)  # wait for any pending operations to clear

globals.print_params(EMAIL_COUNT)

print('* * * * * * * * * * * * * *  P R E T Z E L  P L U S  * * * * * * * * * * * * * *')

for domain, server in globals.DOMAIN_SERVER_MAP.items():
    server.set_privacy_mode("pretzel_plus")

for user in users:
    user.set_privacy_mode("pretzel_plus")

globals.reset_params()

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

print_stats(constants.PRETZEL_PLUS)

time.sleep(5)  # wait for any pending operations to clear

globals.print_params(EMAIL_COUNT)
