from eosfactory.eosf import *
import time
import unittest


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
class TestStringMethods(unittest.TestCase):
    # def setUp(self):



    def test_deferred(self):
        token_host.push_action(
            "transfer",
            {
                "from": charlie, "to": locktimer,
                "quantity": "0.0150 EOS", "memo":"createtimer"
            },
            charlie)
        locktimer.table("timerv1", locktimer);

        locktimer.push_action (
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
        self.assertEqual('foo'.upper(), 'FOO')

    # def teardown(self) {
    #     token_host.push_action(
    #         ""
    #     )
    # }
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()

stop()
