# Lock timer
EOS smart contract that allows you to lock eos for a certain amount of time and then they will be automaticaly released.


## Build

You need to have eos ctd 1.6.3 installed

cd scripts
bash compile.sh

## Run tests.

You need to have python 3 and eosfactory installed https://eosfactory.io/build/html/tutorials/01.InstallingEOSFactory.html

cd tests
python3 build.py
python3 test.py

## Actions:

* On transfer (ontransfer). Requires: none.

Event listener on eosio::transfer. If memo is "createtimer" it will create record in timer table with sender, quantity - fee, issent false, everything will be empty . If memo is "replenish", it will accept money. Otherwise transaction will be canceled.
Requirements to createtimer: Quantity must be at least 0.0500 EOS or more. Also there is a fee 0.0300 EOS for creating record costs.

* Lock money (lock). Requires:
  * eosio::name sender (Sender that created record by transfer),
  * uint64_t id (Id of record created by transfer),
  * eosio::name receiver (Future receiver of locked funds),
  * uint32_t date (Date when you want fund to be released in unix time format)

This action locks money and sends deferred transaction with delay date - now(). Max delay is 2 years.
Modifies record, sets receiver, start date, end date (date from func args) and sets issent to true.

* Cancel timer (cancel). Requires:
  * eosio::name sender (Sender that created record by transfer),
  * uint64_t id (Id of record created by transfer)

If timer isn't sent yet (lock() action wasn't called) then you can cancel timer and get your money back (minus fee).

* Claim money (claimmoney). Requires:
  * eosio::name receiver (Receiver of money in the record)
  * uint64_t id (Id of the record),

If the deferred transaction has failed for any reason you can manually claim your money on condition that date of release is already passed.

* Ping (ping). Requires:
  * eosio::name name.

Just checks if contract is working

# Internal actions

* Auto send (autosend). Requires:
  * uint64_t id

Action that fired by deferred transaction to automaticly send money to the receiver. Can be called only by contract itself.

* Deferred transaction (defertxn). Requires:
  * uint32_t delay
  * uint64_t send_id (deferred transaction id)
  * uint64_t id (Id of record associated with this deferred transaction)

Action that is needed to get around 45 days delay limit. It recursively calles itself through 45 days until left delay is less than 45 days.
