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

        time.sleep(7);
        lockConsole()
        locktimer.table("timerv1", locktimer);
        js = correct(getVal());
        arr = js["rows"]
        self.assertEqual(len(arr), 0)
    def test_cancel_locking(self):
        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer,
                "quantity": "0.0213 EOS", "memo":"createtimer"
            },
            bob)
        for i in range(7):
            token_host.push_action(
                "transfer",
                {
                    "from": charlie, "to": locktimer,
                    "quantity": "0.0" + str(i) + "53 EOS", "memo":"createtimer"
                },
                charlie)

        lockConsole()
        locktimer.table("timerv1", locktimer);
        js = correct(getVal());
        arr = js["rows"]
        for i in range(len(arr)):
            self.assertEqual(arr[i]["id"], i)
            self.assertFalse(arr[i]["is_sent"])
        locktimer.push_action (
            "cancel",
            {
                "sender": bob,
                "id": 0
            },
            permission=(bob, Permission.ACTIVE))
        for i in range(1, 4):
            locktimer.push_action (
                "cancel",
                {
                    "sender": charlie,
                    "id": i
                },
                permission=(charlie, Permission.ACTIVE))
        lockConsole()
        locktimer.table("timerv1", locktimer);
        js = correct(getVal());
        arr = js["rows"]
        for i in range(len(arr)):
            self.assertNotEqual(arr[i]["id"], i)
            self.assertFalse(arr[i]["is_sent"])
        for i in range(4, 8):
            locktimer.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": i,
                    "receiver": zoro,
                    "date": now() + int(10)
                },
                permission=(charlie, Permission.ACTIVE))
        lockConsole()
        locktimer.table("timerv1", locktimer);
        js = correct(getVal());
        arr = js["rows"]
        for i in range(len(arr)):
            self.assertTrue(arr[i]["is_sent"])
            self.assertTrue(arr[i]["receiver"] == "zoro")
        time.sleep(10)
        lockConsole()
        locktimer.table("timerv1", locktimer);
        js = correct(getVal());
        arr = js["rows"]
        self.assertTrue(len(arr) == 0);
        lockConsole()
        token_host.table("accounts", zoro)
        js = correct(getVal())["rows"];
        self.assertFalse('0.0000 EOS' in js[0]["balance"])

    def test_restrictions(self):
        try:
            token_host.push_action(
                "transfer",
                {
                    "from": bob, "to": locktimer,
                    "quantity": "0.0213 EOS", "memo":"createtimer"
                },
                bob)
            locktimer.push_action (
                "lock",
                {
                    "sender": bob,
                    "id": 3,
                    "receiver": zoro,
                    "date": now() + int(10)
                },
                permission=(bob, Permission.ACTIVE))
            self.assertTrue(1 == 0);

        except Error as err:
            self.assertTrue("assertion failure with message" in format(err))
        try:
            locktimer.push_action (
                "lock",
                {
                    "sender": bob,
                    "id": 3,
                    "receiver": zoro,
                    "date": now() + int(10)
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertTrue(1 == 0);
        except Error as err:
            # self.assertTrue("assertion failure with message" in format(err))
            print(Error)
        try:
            locktimer.push_action (
                "lock",
                {
                    "sender": bob,
                    "id": 0,
                    "receiver": zoro,
                    "date": now() + int(3888002)
                },
                permission=(bob, Permission.ACTIVE))
            self.assertTrue(1 == 0);
        except Error as err:
            self.assertTrue("assertion failure with message" in format(err))
        try:
            locktimer.push_action (
                "lock",
                {
                    "sender": bob,
                    "id": 0,
                    "receiver": zoro,
                    "date": now() - int(5)
                },
                permission=(bob, Permission.ACTIVE))
            self.assertTrue(1 == 0);
        except Error as err:
            self.assertTrue("assertion failure with message" in format(err))
            # print(err)
        try:
            locktimer.push_action (
                "lock",
                {
                    "sender": bob,
                    "id": 0,
                    "receiver": zoro,
                    "date": now() - int(5)
                },
                permission=(bob, Permission.ACTIVE))
            self.assertTrue(1 == 0);
        except Error as err:
            self.assertTrue("assertion failure with message" in format(err))
            # print(err)
        locktimer.push_action (
            "lock",
            {
                "sender": bob,
                "id": 0,
                "receiver": zoro,
                "date": now() + int(1000)
            },
            permission=(bob, Permission.ACTIVE))
        try:
            locktimer.push_action (
                "claimmoney",
                {
                    "receiver": zoro,
                    "id": 0
                },
                permission=(zoro, Permission.ACTIVE))
            self.assertTrue(1 == 0);
        except Error as err:
            self.assertTrue("assertion failure with message" in format(err))
        try:
            locktimer.push_action (
                "cancel",
                {
                    "sender": bob,
                    "id": 0
                },
                permission=(bob, Permission.ACTIVE))
            self.assertTrue(1 == 0);
        except Error as err:
            self.assertTrue("assertion failure with message" in format(err))
if __name__ == '__main__':
    unittest.main()

stop()
