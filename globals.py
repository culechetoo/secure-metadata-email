DOMAIN_SERVER_MAP = {}

LOGGING = True

def reset_params():
    global SERVER_BYTES_SENT
    global SERVER_BYTES_RECD
    global CLIENT_BYTES_SENT
    global CLIENT_BYTES_RECD
    global SERVER_TIME
    global CLIENT_TIME
    global TOTAL_TIME
    global PROTOCOL_WISE_BYTES_STATS
    global PROTOCOL_WISE_TIME_STATS
    
    SERVER_BYTES_SENT = 0
    SERVER_BYTES_RECD = 0
    CLIENT_BYTES_SENT = 0
    CLIENT_BYTES_RECD = 0

    PROTOCOL_WISE_BYTES_STATS = {i: {
        "ALICE_BYTES_SENT": 0,
        "ALICE_BYTES_RECD": 0,
        "GOOGL_BYTES_SENT": 0,
        "GOOGL_BYTES_RECD": 0,
        "YAHOO_BYTES_SENT": 0,
        "YAHOO_BYTES_RECD": 0,
        "BOB_BYTES_SENT": 0,
        "BOB_BYTES_RECD": 0
    } for i in range(1, 5)}

    SERVER_TIME = 0
    CLIENT_TIME = 0

    TOTAL_TIME = 0
    PROTOCOL_WISE_TIME_STATS = {i: {
        "ALICE_TIME": 0,
        "GOOGL_TIME": 0,
        "YAHOO_TIME": 0,
        "BOB_TIME": 0
    } for i in range(1, 5)}




def print_params(email_count):
    print()
    print('- - - - - -  S T A T S  - - - - - -')
    print(f"Total time: %.2f s" % TOTAL_TIME)
    print(f"Time per email: %.2f s" % (float(TOTAL_TIME)/float(email_count)))
    print()
    print(f"Bytes sent per email by clients = %.0f" %
          (float(CLIENT_BYTES_SENT)/float(email_count)))
    print(f"Bytes received per email by clients = %.0f" %
          (float(CLIENT_BYTES_RECD)/float(email_count)))
    print(f"Bytes sent per email by servers = %.0f" %
          (float(SERVER_BYTES_SENT)/float(email_count)))
    print(f"Bytes received per email by servers = %.0f" %
          (float(SERVER_BYTES_RECD)/float(email_count)))
    print()

    print(f"Bytes sent per email by ALICE Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_BYTES_STATS[1]["ALICE_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[2]["ALICE_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[3]["ALICE_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[4]["ALICE_BYTES_SENT"]) / float(email_count)))
    print(f"Bytes sent per email by GOOGL Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_BYTES_STATS[1]["GOOGL_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[2]["GOOGL_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[3]["GOOGL_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[4]["GOOGL_BYTES_SENT"]) / float(email_count)))
    print(f"Bytes sent per email by YAHOO Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_BYTES_STATS[1]["YAHOO_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[2]["YAHOO_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[3]["YAHOO_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[4]["YAHOO_BYTES_SENT"]) / float(email_count)))
    print(f"Bytes sent per email by BOB Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_BYTES_STATS[1]["BOB_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[2]["BOB_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[3]["BOB_BYTES_SENT"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[4]["BOB_BYTES_SENT"]) / float(email_count)))
    print()

    print(f"Bytes received per email by ALICE Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_BYTES_STATS[1]["ALICE_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[2]["ALICE_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[3]["ALICE_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[4]["ALICE_BYTES_RECD"]) / float(email_count)))
    print(f"Bytes received per email by GOOGL Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_BYTES_STATS[1]["GOOGL_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[2]["GOOGL_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[3]["GOOGL_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[4]["GOOGL_BYTES_RECD"]) / float(email_count)))
    print(f"Bytes received per email by YAHOO Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_BYTES_STATS[1]["YAHOO_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[2]["YAHOO_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[3]["YAHOO_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[4]["YAHOO_BYTES_RECD"]) / float(email_count)))
    print(f"Bytes received per email by BOB Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_BYTES_STATS[1]["BOB_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[2]["BOB_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[3]["BOB_BYTES_RECD"]) / float(email_count),
           float(PROTOCOL_WISE_BYTES_STATS[4]["BOB_BYTES_RECD"]) / float(email_count)))
    print()

    print()
    print(f"CPU time per email for clients = %.5f s" %
          (float(CLIENT_TIME)/float(email_count)))
    print(f"CPU time per email for servers = %.5f s" %
          (float(SERVER_TIME)/float(email_count)))
    print()

    print(f"CPU time email for ALICE Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_TIME_STATS[1]["ALICE_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[2]["ALICE_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[3]["ALICE_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[4]["ALICE_TIME"]) / float(email_count)))
    print(f"CPU time email for GOOGL Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_TIME_STATS[1]["GOOGL_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[2]["GOOGL_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[3]["GOOGL_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[4]["GOOGL_TIME"]) / float(email_count)))
    print(f"CPU time email for YAHOO Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_TIME_STATS[1]["YAHOO_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[2]["YAHOO_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[3]["YAHOO_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[4]["YAHOO_TIME"]) / float(email_count)))
    print(f"CPU time email for BOB Step 1: %.0f Step 2: %.0f Step 3: %.0f Step 4: %.0f" %
          (float(PROTOCOL_WISE_TIME_STATS[1]["BOB_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[2]["BOB_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[3]["BOB_TIME"]) / float(email_count),
           float(PROTOCOL_WISE_TIME_STATS[4]["BOB_TIME"]) / float(email_count)))
    print()
    