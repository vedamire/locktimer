from eosfactory.eosf import *
reset()
testnet = get_testnet("myjungle")
testnet.configure()
master = create_master_account(testnet);

host = new_account(
    master, buy_ram_kbytes=INITIAL_RAM_KBYTES,
    stake_net=INITIAL_STAKE_NET, stake_cpu=INITIAL_STAKE_CPU)
        # cls.alice = new_account(
        #     cls.master, buy_ram_kbytes=INITIAL_RAM_KBYTES,
        #     stake_net=INITIAL_STAKE_NET, stake_cpu=INITIAL_STAKE_CPU)
        # cls.carol = new_account(

host.set_account_permission(Permission.ACTIVE, add_code=True)

timer = Contract(host, "/home/ally/contracts/locktimer")

timer.deploy(payer=master)
