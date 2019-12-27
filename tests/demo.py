from eosfactory.eosf import *
import time
import unittest
import sys, io
import json
import string
stdout = sys.stdout

def now():
    return int(time.time())

def lockConsole():
    sys.stdout = io.StringIO()
def getVal():
    val = sys.stdout.getvalue()
    sys.stdout = stdout
    return val
def correct(val):
    line = " ".join(val.split())
    printable = set(string.printable)
    line = ''.join(filter(lambda x: x in printable, line))
    in1 = line.index('{')
    in2 = line.rindex('}') + 1
    line = line[in1:-(len(line) - in2)]
    return json.loads(line)

lockConsole()
reset()
create_master_account("master")

create_account("token_host", master, account_name="eosio.token")
create_account("locktimer", master, account_name="locktimer")

token = Contract(token_host, "/home/ally/contracts/eosio.contracts/contracts/eosio.token")
timer = Contract(locktimer, "/home/ally/contracts/locktimer")

locktimer.set_account_permission(Permission.ACTIVE, add_code=True)
token_host.set_account_permission(Permission.ACTIVE, add_code=True)


create_account("charlie", master)
create_account("bob", master)
create_account("zoro", master)


token.deploy()
timer.deploy()

token_host.push_action(
    "create",
        {
        "issuer": charlie,
        "maximum_supply": "1000000000.0000 EOS",
        "can_freeze": "0",
        "can_recall": "0",
        "can_whitelist": "0"
    }, [charlie, token_host])

token_host.push_action(
    "issue",
    {
        "to": charlie, "quantity": "100.0000 EOS", "memo": ""
    },
    charlie)

token_host.push_action(
    "transfer",
    {
        "from": charlie, "to": bob,
        "quantity": "50.0000 EOS", "memo":""
    },
    charlie)

getVal();

# --------------------------------------------------
# Creating timer
print("Creating timer")
token_host.push_action(
    "transfer",
    {
        "from": charlie, "to": locktimer,
        "quantity": "0.0750 EOS", "memo":"createtimer"
    },
    charlie)
 # Print created timer
locktimer.table("timerv1", locktimer);
 # Creating another one timer
print("Creating another one")
token_host.push_action(
    "transfer",
    {
        "from": charlie, "to": locktimer,
        "quantity": "0.1750 EOS", "memo":"createtimer"
    },
    charlie)
#  print it
locktimer.table("timerv1", locktimer);

# Sending delayed transaction
print("Sending delayed transaction")

locktimer.push_action (
    "lock",
    {
        "sender": charlie,
        "id": 1,
        "receiver": bob,
        "date": now() + int(20) # after 20 seconds delay
    },
permission=(charlie, Permission.ACTIVE))

# Check all balances
print("Checking tables while locked")

token_host.table("accounts", bob);
token_host.table("accounts", charlie);
token_host.table("accounts", locktimer);

time.sleep(21);

# Checking again
print("Checking tables after unlocked")

token_host.table("accounts", bob);
token_host.table("accounts", charlie);
token_host.table("accounts", locktimer);

locktimer.table("timerv1", locktimer);

# Cancel other
print("Cancel other")

locktimer.push_action (
    "cancel",
    {
        "sender": charlie,
        "id": 0
    },
permission=(charlie, Permission.ACTIVE))

locktimer.table("timerv1", locktimer);
