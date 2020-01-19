// Maximum period of the deferred transaction is 45 days;

#include <eosio/eosio.hpp>
#include <eosio/print.hpp>
#include <eosio/asset.hpp>
#include <eosio/system.hpp>
#include <eosio/transaction.hpp>
#include <eosio/singleton.hpp>


using namespace eosio;

class [[eosio::contract("locktimer")]] locktimer : public eosio::contract {
  private:

    const symbol ecoin_symbol;
    const asset MIN;
    const int LIMIT = 5;
    struct counter {
     uint64_t deferid;
   };

   typedef eosio::singleton<"counter"_n, counter> counter_table;
   counter_table counters;

    struct [[eosio::table]] timer
    {
      uint64_t id;
      name sender;
      name receiver;
      eosio::asset quantity;
      bool is_sent;
      uint32_t start_date;
      uint32_t end_date;
      uint64_t primary_key() const { return id; }
      uint64_t get_secondary_1() const { return sender.value;}
      uint64_t get_secondary_2() const { return receiver.value;}

    };
    typedef eosio::multi_index<"timerv1"_n, timer, indexed_by<"bysender"_n, const_mem_fun<timer, uint64_t, &timer::get_secondary_1>>,
     indexed_by<"byreceiver"_n, const_mem_fun<timer, uint64_t, &timer::get_secondary_2>>> timer_index;

    timer_index table;

    uint32_t now() {
      return current_time_point().sec_since_epoch();
    }


  public:
    using contract::contract;
    locktimer(name receiver, name code, datastream<const char *> ds) : contract(receiver, code, ds), ecoin_symbol("ECOIN", 2),
     MIN(50, this-> ecoin_symbol),
    table(_self, _self.value), counters(_self, _self.value) {}

    [[eosio::on_notify("eosio.token::transfer")]]
    void ontransfer(const name& sender, const name& to, const eosio::asset& quantity, const std::string& memo)
    {
      if (to != get_self() || sender == get_self()) return;
      check(quantity.amount > 0, "When pigs fly");
      if(memo == "createtimer") {
        check(!isLimit(sender) || quantity.symbol == ecoin_symbol, "You have expanded your 5 timers. Wait for release or lock Ecoin without limits");
        if(quantity.symbol == ecoin_symbol) check(quantity >= MIN, "Minimum amount of ecoins is 50");
        uint64_t primary_key = table.available_primary_key();
        table.emplace(get_self(), [&](auto &row) {
          row.id = primary_key;
          row.sender = sender;
          row.receiver = get_self();
          row.quantity = quantity;
          row.is_sent = false;
          row.start_date = NULL;
          row.end_date = NULL;
        });
        print("Timer is created with id: ", primary_key);
      }
       else {
        check(memo == "replenish", "Wrong memo. To transfer money here use ether 'createtimer' or 'replenish' memo");
        print("Account is successfully replenished");
      }
    }

    [[eosio::action]]
    void lock(const name& sender, const uint64_t& id, const name& receiver, const uint32_t& date) {
      require_auth(sender);
      check(is_account(receiver), "Receiver's account doesn't exist");
      check(receiver != get_self(), "Can't set contract itself as a receiver");
      check(now() < date, "The date is already passed");
      const uint32_t twoyears = 31556926 + 31556926;
      check(date - now() <= twoyears, "Maximum delay supported from now is 2 years");
      auto timer = table.find(id);
      check(timer != table.end(), "Timer with this id doesn't exist");
      check(timer->sender == sender, "You are not the owner of this timer");
      check(timer->is_sent == false, "This timer is already locked");
      table.modify(timer, get_self(), [&](auto& row) {
        row.receiver = receiver;
        row.start_date = now();
        row.end_date = date;
        row.is_sent = true;
      });
      send_recursion(timer->end_date - now(), id);
    }

    [[eosio::action]]
    void cancel(const name& sender, const uint64_t& id) {
      require_auth(sender);
      auto timer = table.find(id);
      check(timer != table.end(), "Timer with this id doesn't exist");
      check(timer->sender == sender, "You are not the owner of this timer");
      check(timer->is_sent == false, "Money are already locked and can't be unlocked until the date");

      action{
          permission_level{get_self(), "active"_n},
          "eosio.token"_n,
          "transfer"_n,
          std::make_tuple(get_self(), timer->sender, timer->quantity, std::string("You canceled your timer and got your money!"))
      }.send();
      table.erase(timer);
    }

    [[eosio::action]]
    void autosend(const uint64_t& id) {
      require_auth(get_self());
      auto timer = table.find(id);
      check(timer != table.end(), "There's no wage contract with such an id");
      check(timer->is_sent == true, "The transaction isn't sent yet");
      check(timer->end_date - 1 < now(), "Time isn't passed yet");

      release(timer, table);
    }

    [[eosio::action]]
    void defertxn(const uint32_t& delay, const uint64_t& _id) {
        require_auth(get_self());
        eosio::transaction deferred;
        uint32_t max_delay = 3888000; //max delay supported by EOS 3888000
        if (delay <= max_delay) {
          deferred.actions.emplace_back (
            permission_level{get_self(), "active"_n},
            get_self(), "autosend"_n,
            std::make_tuple(_id)
          );
          deferred.delay_sec = delay;
          deferred.send(updateId(), get_self());
        //perform your transaction here
        }
        else{
            uint32_t remaining_delay = delay - max_delay;
            // transaction to update the delay
            deferred.actions.emplace_back(
                eosio::permission_level{get_self(), "active"_n},
                get_self(),
                "defertxn"_n,
                std::make_tuple(remaining_delay, _id));
            deferred.delay_sec = max_delay; // here we set the new delay which is maximum until remaining_delay is less the max_delay
            deferred.send(updateId(), get_self());
        }
    }

    [[eosio::action]]
    void claimmoney(const name& receiver, const uint64_t& id) {
      require_auth(receiver);
      auto timer = table.find(id);
      check(timer != table.end(), "Timer with this id doesn't exist");
      check(timer->is_sent == true, "Money aren't sent yet");
      check(timer->receiver == receiver, "You are not the receiver of this timer");
      check(timer->end_date - 1 < now(), "Time isn't passed yet");

      release(timer, table);
    }

    [[eosio::action]]
    void ping(const name& name) {
      require_auth(name);
      print("Contract is working");
    }

  private:

    void send_recursion(const uint32_t& delay, const uint64_t& id) {
      action (
        permission_level(get_self(),"active"_n),
        get_self(),
        "defertxn"_n,
        std::make_tuple(delay, id)
      ).send();
    }

    bool isLimit(const name& sender) {
      auto index = table.get_index<"bysender"_n>();
      auto itr = index.lower_bound(sender.value);
      int counter = 0;
      while (itr != index.end() && itr->sender.value == sender.value) {
        if(itr->quantity.symbol != ecoin_symbol) counter += 1;
        itr++;
      }
      return counter >= LIMIT;
    }

    uint64_t updateId() {
      if(!counters.exists()) {
        uint64_t initial = 1000;
        counters.set(counter{initial}, get_self());
        return initial;
      }
      counter count = counters.get();
      counter newcounter = counter{count.deferid + (uint64_t) 1};
      counters.set(newcounter, get_self());
      return newcounter.deferid;
    }

    void release(const timer_index::const_iterator& timer, timer_index& table) {
      action{
        permission_level{get_self(), "active"_n},
        "eosio.token"_n,
        "transfer"_n,
        std::make_tuple(get_self(), timer->receiver, timer->quantity, std::string("Locked money are released!"))
      }.send();
      table.erase(timer);
    }
};
