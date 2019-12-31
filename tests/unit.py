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
create_account("locktimer1", master, account_name="locktimer1")
create_account("locktimer2", master, account_name="locktimer2")
create_account("locktimer3", master, account_name="locktimer3")



token = Contract(token_host, "/home/ally/contracts/eosio.contracts/contracts/eosio.token")
lock = Contract(locktimer, "/home/ally/contracts/locktimer")
lock1 = Contract(locktimer1, "/home/ally/contracts/locktimer")
lock2 = Contract(locktimer2, "/home/ally/contracts/locktimer")
lock3 = Contract(locktimer3, "/home/ally/contracts/locktimer")


locktimer.set_account_permission(Permission.ACTIVE, add_code=True)
locktimer1.set_account_permission(Permission.ACTIVE, add_code=True)
locktimer2.set_account_permission(Permission.ACTIVE, add_code=True)
locktimer3.set_account_permission(Permission.ACTIVE, add_code=True)

token_host.set_account_permission(Permission.ACTIVE, add_code=True)
create_account("charlie", master)
create_account("bob", master)
create_account("zoro", master, account_name="zoro")
token.deploy()
lock.deploy()
lock1.deploy()
lock2.deploy()
lock3.deploy()
token_host.push_action(
    "create",
        {
        "issuer": zoro,
        "maximum_supply": "1000000000.0000 EOS",
        "can_freeze": "0",
        "can_recall": "0",
        "can_whitelist": "0"
    }, [zoro, token_host])

token_host.push_action(
    "issue",
    {
        "to": zoro, "quantity": "100000.0000 EOS", "memo": ""
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
FEE = 0.03

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
        table = locktimer.table("timerv1", locktimer);
        balance = token_host.table("accounts", locktimer);
        afterfee = afterFee(quantity);
        self.assertTrue(table.json["rows"][0]["quantity"] == afterfee);
        self.assertTrue(balance.json["rows"][0]["balance"] == quantity);
        locktimer.push_action(
            "cancel",
            {
                "sender": bob, "id": 0
                # "quantity": quantity, "memo":"createtimer"
            },
            bob)
        balance = token_host.table("accounts", bob);
        self.assertTrue(balance.json["rows"][0]["balance"] == afterFee("50.0000 EOS"));

    def test_single(self):
        quantity = "8.0000 EOS";

        token_host.push_action(
            "transfer",
            {
                "from": bob, "to": locktimer1,
                "quantity": quantity, "memo":"createtimer"
            },
            bob)
        table = locktimer1.table("timerv1", locktimer1);
        balance = token_host.table("accounts", locktimer1);
        afterfee = afterFee(quantity);
        self.assertTrue(table.json["rows"][0]["quantity"] == afterfee);
        self.assertTrue(balance.json["rows"][0]["balance"] == quantity);
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
        balance = token_host.table("accounts", charlie).json["rows"][0]["balance"];
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
        # self.assertEqual(Balance(locktimer2), toStr(toFloat(quantity) * 5));
        rows = Rows(locktimer2);
        for row in rows:
            self.assertEqual(row["quantity"], toStr(toFloat(affee)))

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
                    # "quantity": quantity, "memo":"createtimer"
                },
                charlie)
        self.assertEqual(len(Rows(locktimer3)), 0);
        balance = Balance(charlie);
        total = toStr(toFloat("50.000 EOS") - FEE * 5)
        self.assertEqual(balance, total)
# Check tables modification
    # def test_multiple(self):
    #     # time.sleep(10)
        # for i in range(5):
        #     token_host.push_action(
        #         "transfer",
        #         {
        #             "from": charlie, "to": wageservice1,
        #             "quantity": "" + str(i+4) + ".0300 EOS", "memo":"placewage"
        #         },
        #         charlie);
    #     arr = captureConsole(lambda _: wageservice1.table("wagev1", wageservice1))["rows"];
    #
    #     for i in range(5):
    #         self.assertEqual(arr[i]["id"], i);
    #         self.assertEqual(arr[i]["is_specified"], False);
    #     for i in range(5):
    #         wageservice1.push_action(
    #             "placewage",
    #             {
    #                 "employer": charlie,
    #                 "id": i,
    #                 "worker": bob,
    #                 "days": 4
    #             },
    #             permission=(charlie, Permission.ACTIVE))
    #     arr = captureConsole(lambda _: wageservice1.table("wagev1", wageservice1))["rows"];
    #
    #     for i in range(5):
    #         self.assertEqual(arr[i]["is_accepted"], False);
    #         self.assertEqual(arr[i]["is_specified"], True);
    #         self.assertEqual(arr[i]["worker"], "bob");
    #     for i in range(5):
    #         wageservice1.push_action(
    #             "acceptwage",
    #             {
    #                 "worker": bob,
    #                 "id": i,
    #                 "isaccepted": True
    #             },
    #             permission=(bob, Permission.ACTIVE))
    #     arr = captureConsole(lambda _: wageservice1.table("wagev1", wageservice1))["rows"];
    #     for i in range(5):
    #         # self.assertEqual(arr[i]["id"], i);
    #         self.assertEqual(arr[i]["is_accepted"], True);
    #     for i in range(5):
    #         for r in range(4):
    #             time.sleep(0.5)
    #             wageservice1.push_action(
    #                 "addworkday",
    #                 {
    #                     "employer": charlie,
    #                     "id": i
    #                 },
    #                 permission=(charlie, Permission.ACTIVE));
    #     arr = captureConsole(lambda _: wageservice1.table("wagev1", wageservice1))["rows"];
    #     for i in range(5):
    #         # self.assertEqual(arr[i]["id"], i);
    #         self.assertEqual(arr[i]["worked_days"], 4);
    #     for i in range(5):
    #         wageservice1.push_action(
    #             "closewage",
    #             {
    #                 "employer": charlie,
    #                 "id": i
    #             },
    #             permission=(charlie, Permission.ACTIVE))
        # arr = captureConsole(lambda _: wageservice1.table("wagev1", wageservice1))["rows"];

        # self.assertEqual(getBalance(wageservice1), 0);
        # print(js);
        # def test_double(self):
        #
        #     token_host.push_action(
        #         "transfer",
        #         {
        #             "from": bob, "to": wageservice,
        #             "quantity": "6.0000 EOS", "memo":"placewage"
        #         },
        #         bob)
        #     js = captureConsole(lambda _:wageservice.table("wagev1", wageservice))["rows"][0];
if __name__ == '__main__':
    unittest.main()
