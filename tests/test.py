from eosfactory.eosf import *
import time

def now():
  return int(time.time())
reset()

create_master_account("master")

create_account("token_host", master, account_name="eosio.token")
create_account("locktimer", master, account_name="locktimer")

token = Contract(token_host, "/home/ally/contracts/eosio.contracts/contracts/eosio.token")
timer = Contract(locktimer, "/home/ally/contracts/locktimer")

# locktimer.set_account_permission(
#     Permission.ACTIVE, {
#         "threshold":
#             1,
#         "keys": [{"key": locktimer.active_key.key_public, "weight":1 }],
#         "accounts": [
#             {
#                 "permission":
#                     {
#                         "actor": locktimer,
#                         "permission": "active"
#                     },
#                 "weight": 1
#             },
#             {
#                 "permission":
#                     {
#                         "actor": locktimer,
#                         "permission": "eosio.code"
#                     },
#                 "weight": 1
#             }
#         ]
#     }, Permission.OWNER, (locktimer, Permission.OWNER))
locktimer.set_account_permission(Permission.ACTIVE, add_code=True)
token_host.set_account_permission(Permission.ACTIVE, add_code=True)


# token.build()
# timer.build()

token.deploy()
timer.deploy()

create_account("charlie", master)
create_account("bob", master)

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
        "quantity": "20.0000 EOS", "memo":""
    },
    charlie)

token_host.push_action(
    "transfer",
    {
        "from": charlie, "to": locktimer,
        "quantity": "0.0150 EOS", "memo":"createtimer"
    },
    charlie)

locktimer.table("timerv1", locktimer);

locktimer.push_action(
    "lock",
    {
        "sender": charlie,
        "id": 0,
        "receiver": bob,
        "date": now() + int(6)
    },
     permission=(charlie, Permission.ACTIVE)
)

time.sleep(10);
locktimer.table("timerv1", locktimer);
token_host.table("accounts", bob);
# locktimer.push_action(
#     "claimmoney",
#     {
#         "receiver": bob,
#         "id": 0
#     },
#      permission=(bob, Permission.ACTIVE)
# )
# locktimer.table("timerv1", locktimer);
# token_host.table("accounts", bob);
stop()
