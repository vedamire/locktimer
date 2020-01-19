from eosfactory.eosf import *
import time
import unittest
import sys, io
import json
import string
stdout = sys.stdout

CONTRACT_DIR = "/home/ally/contracts/locktimer"

reset()
create_master_account("master")

create_account("token_host", master, account_name="eosio.token")
# ecointoken12
create_account("ecoin_host", master, account_name="ecointoken12")
create_account("locktimer", master, account_name="locktimer")
create_account("locktimer1", master, account_name="locktimer1")
create_account("locktimer2", master, account_name="locktimer2")
create_account("locktimer3", master, account_name="locktimer3")
create_account("locktimer4", master, account_name="locktimer4")
create_account("locktimer5", master, account_name="locktimer5")
create_account("locktime1r", master, account_name="locktime1r")

token = Contract(token_host, "/home/ally/contracts/eosio.contracts/contracts/eosio.token")
ecoin = Contract(ecoin_host, "/home/ally/contracts/eosio.contracts/contracts/eosio.token")
lock = Contract(locktimer, CONTRACT_DIR)
lock1 = Contract(locktimer1, CONTRACT_DIR)
lock2 = Contract(locktimer2, CONTRACT_DIR)
lock3 = Contract(locktimer3, CONTRACT_DIR)
lock4 = Contract(locktimer4, CONTRACT_DIR)
lock5 = Contract(locktimer5, CONTRACT_DIR)
lock6 = Contract(locktime1r, CONTRACT_DIR)

locktimer.set_account_permission(Permission.ACTIVE, add_code=True)
locktimer1.set_account_permission(Permission.ACTIVE, add_code=True)
locktimer2.set_account_permission(Permission.ACTIVE, add_code=True)
locktimer3.set_account_permission(Permission.ACTIVE, add_code=True)
locktimer4.set_account_permission(Permission.ACTIVE, add_code=True)
locktimer5.set_account_permission(Permission.ACTIVE, add_code=True)
locktime1r.set_account_permission(Permission.ACTIVE, add_code=True)

token_host.set_account_permission(Permission.ACTIVE, add_code=True)
create_account("charlie", master)
create_account("bob", master)
create_account("zoro", master, account_name="zoro")
token.deploy()
ecoin.deploy()
lock.deploy()
lock1.deploy()
lock2.deploy()
lock3.deploy()
lock4.deploy()
lock5.deploy()
lock6.deploy()
token_host.push_action(
    "create",
        {
        "issuer": zoro,
        "maximum_supply": "1000000000.0000 EOS",
        "can_freeze": "0",
        "can_recall": "0",
        "can_whitelist": "0"
    }, [zoro, token_host])
ecoin_host.push_action(
    "create",
        {
        "issuer": zoro,
        "maximum_supply": "1000000000.00 ECOIN",
        "can_freeze": "0",
        "can_recall": "0",
        "can_whitelist": "0"
    }, [zoro, ecoin_host])
token_host.push_action(
    "issue",
    {
        "to": zoro, "quantity": "100000.0000 EOS", "memo": ""
    },
    permission=(zoro, Permission.ACTIVE))

ecoin_host.push_action(
    "issue",
    {
        "to": zoro, "quantity": "100000.00 ECOIN", "memo": ""
    },
    permission=(zoro, Permission.ACTIVE))

token_host.push_action(
    "create",
        {
        "issuer": zoro,
        "maximum_supply": "1000000000.00 ECOIN",
        "can_freeze": "0",
        "can_recall": "0",
        "can_whitelist": "0"
    }, [zoro, token_host])

token_host.push_action(
    "issue",
    {
        "to": zoro, "quantity": "100000.00 ECOIN", "memo": ""
    },
    permission=(zoro, Permission.ACTIVE))
# token_host.push_action(
#     "issue",
#     {
#         "to": bob, "quantity": "1000000.0000 EOS", "memo": ""
#     },
#     zoro)
token_host.push_action(
    "transfer",
    {
        "from": zoro, "to": charlie,
        "quantity": "50.0000 EOS", "memo":""
    },
    zoro)
token_host.push_action(
    "transfer",
    {
        "from": zoro, "to": bob,
        "quantity": "50.0000 EOS", "memo":""
    },
    zoro)
FEE = 0.00;
LIMIT = 5;
def getBase(body):
    str_charl = str(body);
    dots = str_charl[str_charl.find(".") + 1:];
    ch_base = " EOS"
    for i in range(4 - len(dots)):
        ch_base = "0" + ch_base;
    return ch_base;
def afterFee(quantity):
    afterfee = float(quantity.replace(" EOS", "")) - FEE;
    return str(afterfee) + getBase(afterfee)
def toFloat(quantity):
    return float(quantity.replace(" EOS", ""));
def toStr(quantity):
    return str(quantity) + getBase(quantity);
def Balance(name):
    return token_host.table("accounts", name).json["rows"][0]["balance"]
def Rows(contract):
    return contract.table("timerv1", contract).json["rows"];
def now():
    return int(time.time())
class TestStringMethods(unittest.TestCase):
    # def tearDown(self):
    #     stop();

    def setUp(self):

        time.sleep(1);

        # print(chb)
        balance = Balance(charlie)
        # self.assertEqual(table.json["rows"][0]["board"][0], 0)
        # amount = table.json["rows"][0].balance; table.json["rows"][0]["balance"],
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": zoro,
                "quantity": balance, "memo":""
            },
            charlie)
        balance = Balance(bob);
        token_host.push_action(
            "transfer",
            {
                "from": zoro, "to": charlie,
                "quantity": "50.0000 EOS", "memo":""
            },
            zoro)
        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": zoro,
                "quantity": balance, "memo":""
            },
            bob)
        token_host.push_action(
            "transfer",
            {
                "from": zoro, "to": bob,
                "quantity": "50.0000 EOS", "memo":""
            },
            zoro)

    def test_limit(self):
        # locktimer6
        for i in range(5):
            ecoin_host.push_action(
                "transfer",
                {
                    "from": zoro, "to": locktime1r,
                    "quantity": str(i+1) + "00.00 ECOIN", "memo":"createtimer"
                },
                zoro);
            token_host.push_action(
                "transfer",
                {
                    "from": zoro, "to": locktime1r,
                    "quantity": str(i+1) + ".0000 EOS", "memo":"createtimer"
                },
                zoro);
        try:
            token_host.push_action(
                "transfer",
                {
                    "from": zoro, "to": locktime1r,
                    "quantity": "0.9821 EOS" , "memo":"createtimer"
                },
                zoro);
            self.assertEqual("Creating timer out of bound", "");
        except Error as err:
            self.assertTrue("You have expanded your 5 timers. Lock Ecoin without limits" in err.message)
            print("timers bound passed")

        try:
            token_host.push_action(
                "transfer",
                {
                    "from": zoro, "to": locktime1r,
                    "quantity": "101.00 ECOIN" , "memo":"createtimer"
                },
                zoro);
            self.assertEqual("Creating timer without checking contract", "");
        except Error as err:
            self.assertTrue("You have expanded your 5 timers. Lock Ecoin without limits" in err.message)
            print("timers contract passed")
        try:
            ecoin_host.push_action(
                "transfer",
                {
                    "from": zoro, "to": locktime1r,
                    "quantity": "2.00 ECOIN" , "memo":"createtimer"
                },
                zoro);
            self.assertEqual("creating ecoins timer without minimum", "");
        except Error as err:
            self.assertTrue("Minimum amount" in err.message)
            print("timers ecoin minimum passed")
        ecoin_host.push_action(
            "transfer",
            {
                "from": zoro, "to": locktime1r,
                "quantity": "103.00 ECOIN" , "memo":"createtimer"
            },
            zoro);
    def test_token(self):
        ecoin_host.push_action(
            "transfer",
            {
                "from": zoro, "to": bob,
                "quantity": "1000.00 ECOIN", "memo":""
            },
            zoro)
        quantity = "100.00 ECOIN";
        ecoin_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer,
                "quantity": quantity, "memo":"createtimer"
            },
            bob)

        # afterfee = afterFee(quantity);
        self.assertTrue(Rows(locktimer)[0]["quantity"] == quantity and Rows(locktimer)[0]["token"] == "ecointoken12");
        # self.assertTrue(Balance(locktimer) == quantity);
        locktimer.push_action(
            "cancel",
            {
                "sender": bob, "id": 0
                # "quantity": quantity, "memo":"createtimer"
            },
            bob)
        balance = ecoin_host.table("accounts", bob).json["rows"][0]["balance"]
        self.assertTrue(balance == "1000.00 ECOIN");
        charlie_qty = "200.00 ECOIN";
        ecoin_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer,
                "quantity": charlie_qty, "memo":"createtimer"
            },
            bob)

        # afterfee = afterFee(quantity);
        self.assertTrue(Rows(locktimer)[0]["quantity"] == charlie_qty and Rows(locktimer)[0]["token"] == "ecointoken12");
        locktimer.push_action (
            "lock",
            {
                "sender": bob,
                "id": 0,
                "receiver": charlie,
                "date": now() + int(4)
            },
            permission=(bob, Permission.ACTIVE))
        time.sleep(4);
        self.assertEqual(len(Rows(locktimer)), 0);

        balance = ecoin_host.table("accounts", charlie).json["rows"][0]["balance"]
        self.assertEqual(charlie_qty, balance);
    def test_cancel(self):
        # time.sleep(1)
        quantity = "6.0000 EOS";
        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer,
                "quantity": quantity, "memo":"createtimer"
            },
            bob)

        # afterfee = afterFee(quantity);
        self.assertTrue(Rows(locktimer)[0]["quantity"] == quantity);
        # self.assertTrue(Balance(locktimer) == quantity);
        locktimer.push_action(
            "cancel",
            {
                "sender": bob, "id": 0
                # "quantity": quantity, "memo":"createtimer"
            },
            bob)
        self.assertTrue(Balance(bob) == afterFee("50.0000 EOS"));

    def test_single(self):
        quantity = "8.0000 EOS";

        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer1,
                "quantity": quantity, "memo":"createtimer"
            },
            bob)
        self.assertEqual(len(Rows(locktimer1)), 1);
        afterfee = afterFee(quantity);
        self.assertTrue(Rows(locktimer1)[0]["quantity"] == afterfee);
        locktimer1.push_action (
            "lock",
            {
                "sender": bob,
                "id": 0,
                "receiver": charlie,
                "date": now() + int(6)
            },
            permission=(bob, Permission.ACTIVE))
        time.sleep(6);
        self.assertEqual(len(Rows(locktimer1)), 0);

        balance = Balance(charlie);
        res = toStr(toFloat("50.0000 EOS") + toFloat(afterFee(quantity)));
        self.assertEqual(res, balance);

    def test_multiple(self):
        quantity = "7.0000 EOS";
        affee = afterFee(quantity);
        for i in range(5):
            time.sleep(1)
            token_host.push_action(
                "transfer",
                {
                    "from": charlie, "to": locktimer2,
                    "quantity": quantity, "memo":"createtimer"
                },
                charlie);
        rows = Rows(locktimer2);
        for i in range(5):
            self.assertEqual(rows[i]["quantity"], toStr(toFloat(affee)))

        for i in range(5):
            # time.sleep(1)
            locktimer2.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": i,
                    "receiver": bob,
                    "date": now() + int(6)
                },
                permission=(charlie, Permission.ACTIVE))
        time.sleep(6);
        self.assertEqual(len(Rows(locktimer2)), 0);

        balance = Balance(bob);
        total = toStr(toFloat("50.000 EOS") + toFloat(affee) * 5)
        self.assertEqual(balance, total)

    def test_multiple_cancel(self):
        quantity = "4.0000 EOS";
        affee = afterFee(quantity);
        for i in range(5):
            time.sleep(1)
            token_host.push_action(
                "transfer",
                {
                    "from": charlie, "to": locktimer3,
                    "quantity": quantity, "memo":"createtimer"
                },
                charlie);

        rows = Rows(locktimer3);

        for i in range(5):
            self.assertEqual(rows[i]["quantity"], toStr(toFloat(affee)))
        for i in range(5):
            locktimer3.push_action(
                "cancel",
                {
                    "sender": charlie, "id": i
                },
                charlie)
        self.assertEqual(len(Rows(locktimer3)), 0);
        balance = Balance(charlie);
        total = toStr(toFloat("50.000 EOS") - FEE * 5)
        self.assertEqual(balance, total)
    def test_ext_errors(self):
        # try:
        #     token_host.push_action(
        #         "transfer",
        #         {
        #             "from": charlie, "to": locktimer4,
        #             "quantity": "0.0200 EOS", "memo":"createtimer"
        #         },
        #         charlie);
        #     self.assertEqual("Transfering below MIN 0.0200 EOS", "");
        # except Error as err:
        #     self.assertTrue("Minimum amount of deposit is 0.0500 EOS" in err.message)
        #     print("min passed")
        try:
            token_host.push_action(
                "transfer",
                {
                    "from": charlie, "to": locktimer4,
                    "quantity": "0.0900 EOS", "memo":"wrongmemo"
                },
                charlie);
            self.assertEqual("transfering with wrong memo", "");
        except Error as err:
            self.assertTrue("Wrong memo. To transfer money here use ether 'createtimer' or 'replenish' memo" in err.message)
            print("wrong memo passed")
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer4,
                "quantity": "0.0900 EOS", "memo":"createtimer"
            },
            charlie);

        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer4,
                "quantity": "0.0800 EOS", "memo":"createtimer"
            },
            charlie);
        locktimer4.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 1,
                "receiver": bob,
                "date": now() + int(1000)
            }, charlie)

        try:
            locktimer4.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": 0,
                    "receiver": bob,
                    "date": now() + int(6)
                })
            self.assertEqual("Locking without auth", "");
        except Error as err:
            self.assertTrue("missing authority of charlie" in err.message)
            print("lock auth passed")
        try:
            locktimer4.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": 0,
                    "receiver": "marva",
                    "date": now() + int(6)
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertEqual("Locking to unexisting receiver", "");
        except Error as err:
            self.assertTrue("Receiver's account doesn't exist" in err.message)
            print("lock wrong receiver passed")

        try:
            locktimer4.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": 0,
                    "receiver": locktimer4,
                    "date": now() + int(6)
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertEqual("Locking with receiver contract itself", "");
        except Error as err:
            self.assertTrue("Can't set contract itself as a receiver" in err.message)
            print("lock contract receiver passed")

        try:
            locktimer4.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": 0,
                    "receiver": bob,
                    "date": now() - int(6)
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertEqual("Locking with passed date", "");
        except Error as err:
            self.assertTrue("The date is already passed" in err.message)
            print("lock date passed")

        try:
            locktimer4.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": 0,
                    "receiver": bob,
                    "date": now() + int(71556926)
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertEqual("Locking with date > 2 years", "");
        except Error as err:
            self.assertTrue("Maximum delay supported from now is 2 years" in err.message)
            print("lock date > 2 years passed")
        try:
            locktimer4.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": 5,
                    "receiver": bob,
                    "date": now() + int(6)
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertEqual("Locking with not existing id", "");
        except Error as err:
            self.assertTrue("Timer with this id doesn't exist" in err.message)
            print("lock wrong id passed")

        try:
            locktimer4.push_action (
                "lock",
                {
                    "sender": bob,
                    "id": 0,
                    "receiver": bob,
                    "date": now() + int(6)
                },
                permission=(bob, Permission.ACTIVE))
            self.assertEqual("Locking without ownership", "");
        except Error as err:
            self.assertTrue("You are not the owner of this timer" in err.message)
            print("lock ownership passed")

        try:
            time.sleep(0.5)
            locktimer4.push_action (
                "lock",
                {
                    "sender": charlie,
                    "id": 1,
                    "receiver": bob,
                    "date": now() + int(1000)
                }, charlie)
            self.assertEqual("Locking alredy locked", "");

        except Error as err:
            self.assertTrue("This timer is already locked" in err.message);
            print("locking unlocked passed");
        try:
            locktimer4.push_action (
                "cancel",
                {
                    "sender": charlie,
                    "id": 0
                })
            self.assertEqual("Cancel without auth", "");
        except Error as err:
            self.assertTrue("missing authority of charlie" in err.message)

            print("cancel auth passed")

        try:
            locktimer4.push_action (
                "cancel",
                {
                    "sender": charlie,
                    "id": 4
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertEqual("Cancel with wrong id", "");
        except Error as err:
            self.assertTrue("Timer with this id doesn't exist" in err.message)

            print("cancel wrong id passed")
        try:
            locktimer4.push_action (
                "cancel",
                {
                    "sender": bob,
                    "id": 0
                },
                permission=(bob, Permission.ACTIVE))
            self.assertEqual("Cancel without ownership", "");
        except Error as err:
            self.assertTrue("You are not the owner of this timer" in err.message)

            print("cancel ownership passed")

        try:
            locktimer4.push_action (
                "cancel",
                {
                    "sender": charlie,
                    "id": 1
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertEqual("Cancel already sent timer", "");
        except Error as err:
            self.assertTrue("Money are already locked and can't be unlocked until the date" in err.message)

            print("cancel unsent passed")

        try:
            locktimer4.push_action (
                "claimmoney",
                {
                    "receiver": bob,
                    "id": 1
                })
            self.assertEqual("Claim without auth", "");
        except Error as err:
            self.assertTrue("missing authority of bob" in err.message)

            print("claim auth passed")

        try:
            locktimer4.push_action (
                "claimmoney",
                {
                    "receiver": bob,
                    "id": 5
                },
                permission=(bob, Permission.ACTIVE))
            self.assertEqual("Claim with wrong id", "");
        except Error as err:
            self.assertTrue("Timer with this id doesn't exist" in err.message)

            print("claim wrong id passed")

        try:
            locktimer4.push_action (
                "claimmoney",
                {
                    "receiver": bob,
                    "id": 0
                },
                permission=(bob, Permission.ACTIVE))
            self.assertEqual("Claim didn't sent timer", "");
        except Error as err:
            self.assertTrue("Money aren't sent yet" in err.message)

            print("claim unsent passed")

        try:
            locktimer4.push_action (
                "claimmoney",
                {
                    "receiver": charlie,
                    "id": 1
                },
                permission=(charlie, Permission.ACTIVE))
            self.assertEqual("Claiming by not a receiver", "");
        except Error as err:
            self.assertTrue("You are not the receiver of this timer" in err.message)

            print("claim receiver passed")
        try:
            locktimer4.push_action (
                "claimmoney",
                {
                    "receiver": bob,
                    "id": 1
                },
                permission=(bob, Permission.ACTIVE))
            self.assertEqual("Cancel with haven't passed date", "");
        except Error as err:
            self.assertTrue("Time isn't passed yet" in err.message)

            print("cancel date passed")
    def test_int_errors(self):
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer5,
                "quantity": "0.0900 EOS", "memo":"createtimer"
            },
            charlie);

        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer5,
                "quantity": "0.0800 EOS", "memo":"createtimer"
            },
            charlie);
        locktimer5.push_action (
            "lock",
            {
                "sender": charlie,
                "id": 1,
                "receiver": bob,
                "date": now() + int(1000)
            }, charlie)
        try:
            locktimer5.push_action (
                "autosend",
                {
                    "id": 1,
                },
                permission=(bob, Permission.ACTIVE))
            self.assertEqual("Accessed to autosend from outside", "");
        except Error as err:
            self.assertTrue("missing authority of locktimer5" in err.message)
            print("autosend passed")
        try:
            locktimer5.push_action (
                "autosend",
                {
                    "id": 5,
                },
                permission=(locktimer5, Permission.ACTIVE))
            self.assertEqual("autosend wrong id", "");
        except Error as err:
            self.assertTrue("There's no wage contract with such an id" in err.message)
            print("autosend wrong id passed")
        try:
            locktimer5.push_action (
                "autosend",
                {
                    "id": 0,
                },
                permission=(locktimer5, Permission.ACTIVE))
            self.assertEqual("autosend unsent timer", "");
        except Error as err:
            self.assertTrue("The transaction isn't sent yet" in err.message)
            print("autosend wrong id passed")

        try:
            locktimer5.push_action (
                "autosend",
                {
                    "id": 1,
                },
                permission=(locktimer5, Permission.ACTIVE))
            self.assertEqual("autosend didn't passed time", "");
        except Error as err:
            self.assertTrue("Time isn't passed yet" in err.message)
            print("autosend time passed")


        try:
            locktimer5.push_action (
                "defertxn",
                {
                    "delay": 100,
                    "sendid": 0,
                    "_id": 0
                },
                permission=(bob, Permission.ACTIVE))
            self.assertEqual("Accessed to defertxn from outside", "");
        except Error as err:
            self.assertTrue("missing authority of locktimer5" in err.message)

            print("defertxn passed")
            # self.assertTrue("assertion failure with message" in format(err))

if __name__ == '__main__':
    unittest.main()
