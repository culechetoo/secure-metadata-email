DOMAIN_SERVER_MAP = {}

def reset_params():
    global SERVER_BYTES_SENT
    global SERVER_BYTES_RECD
    global CLIENT_BYTES_SENT
    global CLIENT_BYTES_RECD
    global SERVER_TIME
    global CLIENT_TIME
    
    SERVER_BYTES_SENT = 0
    SERVER_BYTES_RECD = 0
    CLIENT_BYTES_SENT = 0
    CLIENT_BYTES_RECD = 0

    SERVER_TIME = 0
    CLIENT_TIME = 0


def print_params(email_count):
    print(f"Bytes sent per email by clients = %.0f" %
          (float(CLIENT_BYTES_SENT)/float(email_count)))
    print(f"Bytes received per email by clients = %.0f" %
          (float(CLIENT_BYTES_RECD)/float(email_count)))
    print(f"Bytes sent per email by servers = %.0f" %
          (float(SERVER_BYTES_SENT)/float(email_count)))
    print(f"Bytes received per email by servers = %.0f" %
          (float(SERVER_BYTES_RECD)/float(email_count)))
    print()
    print(f"CPU time per email for clients = %.5f s" %
          (float(CLIENT_TIME)/float(email_count)))
    print(f"CPU time per email for servers = %.5f s" %
          (float(SERVER_TIME)/float(email_count)))
    print()
    