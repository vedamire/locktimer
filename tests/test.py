from eosfactory.eosf import *
import time
import unittest
import sys, io
import json
import string
stdout = sys.stdout

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

class TestStringMethods(unittest.TestCase):
    def setUp(self):
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
    def test_single(self):
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0750 EOS", "memo":"createtimer"
            },
            charlie)
        lockConsole()
        locktimer.table("timerv1", locktimer);
        self.assertTrue("0.0750 EOS" in getVal())
        locktimer.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 0,
                "receiver": bob,
                "date": now() + int(6)
            },
            permission=(charlie, Permission.ACTIVE))

        time.sleep(10);
        lockConsole();
        locktimer.table("timerv1", locktimer);
        self.assertTrue('[]' in getVal());

        lockConsole()
        token_host.table("accounts", bob)
        self.assertTrue("0750 EOS" in getVal());
        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": charlie,
                "quantity": "0.0750 EOS", "memo":"createtimer"
            },
            bob)

    def test_cancel(self):

        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer,
                "quantity": "0.0250 EOS", "memo":"createtimer"
            },
            bob)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0350 EOS", "memo":"createtimer"
            },
            charlie)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0370 EOS", "memo":"createtimer"
            },
            charlie)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0320 EOS", "memo":"createtimer"
            },
            charlie)


        lockConsole()
        locktimer.table("timerv1", locktimer);
        self.assertTrue('"id": 0,' in getVal())

        locktimer.push_action (
            "cancel",
            {
                "sender": charlie,
                "id": 2
            },
            permission=(charlie, Permission.ACTIVE))

        locktimer.push_action (
            "cancel",
            {
                "sender": bob,
                "id": 0
            },
            permission=(bob, Permission.ACTIVE))
        lockConsole()
        locktimer.table("timerv1", locktimer);
        val = getVal()
        self.assertTrue('"id": 3,' in val)
        self.assertFalse('"id": 2,' in val)
        self.assertFalse('"id": 0,' in val)
        self.assertTrue('"id": 1,' in val);
        locktimer.push_action (
            "cancel",
            {
                "sender": charlie,
                "id": 3
            },
            permission=(charlie, Permission.ACTIVE))
        locktimer.push_action (
            "cancel",
            {
                "sender": charlie,
                "id": 1
            },
            permission=(charlie, Permission.ACTIVE))
        lockConsole()
        locktimer.table("timerv1", locktimer);
        val = getVal()
        self.assertFalse('"id": 3,' in val)
        self.assertFalse('"id": 1,' in val)

        # 750

        # self.assertTrue('FOO'.isupper())
        # self.assertFalse('Foo'.isupper())

    def test_multiple(self):

        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer,
                "quantity": "0.0253 EOS", "memo":"createtimer"
            },
            bob)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0353 EOS", "memo":"createtimer"
            },
            charlie)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0372 EOS", "memo":"createtimer"
            },
            charlie)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0321 EOS", "memo":"createtimer"
            },
            charlie)
        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer,
                "quantity": "0.0258 EOS", "memo":"createtimer"
            },
            bob)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0352 EOS", "memo":"createtimer"
            },
            charlie)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0379 EOS", "memo":"createtimer"
            },
            charlie)
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0320 EOS", "memo":"createtimer"
            },
            charlie)

        lockConsole()
        locktimer.table("timerv1", locktimer);
        js = correct(getVal());
        # print(js);
        arr = js["rows"]
        for i in range(len(arr)):
            self.assertEqual(arr[i]["id"], i)
            self.assertFalse(arr[i]["is_sent"])

        locktimer.push_action (
            "lock",
            {
                "sender": bob,
                "id": 0,
                "receiver": charlie,
                "date": now() + int(6)
            },
            permission=(bob, Permission.ACTIVE))
        locktimer.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 1,
                "receiver": bob,
                "date": now() + int(6)
            },
            permission=(charlie, Permission.ACTIVE))
        locktimer.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 2,
                "receiver": bob,
                "date": now() + int(6)
            },
            permission=(charlie, Permission.ACTIVE))
        locktimer.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 3,
                "receiver": bob,
                "date": now() + int(6)
            },
            permission=(charlie, Permission.ACTIVE))
        locktimer.push_action (
            "lock",
            {
                "sender": bob,
                "id": 4,
                "receiver": bob,
                "date": now() + int(6)
            },
            permission=(bob, Permission.ACTIVE))
        locktimer.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 5,
                "receiver": bob,
                "date": now() + int(6)
            },
            permission=(charlie, Permission.ACTIVE))
        locktimer.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 6,
                "receiver": bob,
                "date": now() + int(6)
            },
            permission=(charlie, Permission.ACTIVE))
        locktimer.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 7,
                "receiver": bob,
                "date": now() + int(6)
            },
            permission=(charlie, Permission.ACTIVE))
        lockConsole()
        locktimer.table("timerv1", locktimer);
        js = correct(getVal());
        arr = js["rows"]
        for i in range(len(arr)):
            self.assertEqual(arr[i]["id"], i)
            self.assertTrue(arr[i]["is_sent"])
        # lockConsole()
        # locktimer.table("timerv1", locktimer);
        # val = getVal()
        # str3 ='"id": 3,"sender": "charlie", "receiver": "locktimer", "quantity": "0.0150 EOS", "is_sent": 1'
        # str4 ='"id": 2,"sender": "charlie", "receiver": "locktimer", "quantity": "0.0150 EOS", "is_sent": 1'
        # str5 ='"id": 5,"sender": "charlie", "receiver": "locktimer", "quantity": "0.0150 EOS", "is_sent": 1'
        # str6 ='"id": 1,"sender": "charlie", "receiver": "locktimer", "quantity": "0.0150 EOS", "is_sent": 1'
        # self.assertTrue(str3 in val)
        # self.assertTrue(str4 in val)
        # self.assertTrue(str5 in val)
        # self.assertTrue(str6 in val)
        time.sleep(7);
        lockConsole()
        locktimer.table("timerv1", locktimer);
        js = correct(getVal());
        arr = js["rows"]
        self.assertEqual(len(arr), 0)
                # for i in range(len(arr)):
                #     self.assertEqual(arr[i]["id"], i)
                #     self.assertTrue(arr[i]["is_sent"])
        # self.assertFalse(str3 in val)
        # self.assertFalse(str4 in val)
        # self.assertFalse(str5 in val)
        # self.assertFalse(str6 in val)

if __name__ == '__main__':
    unittest.main()

stop()
