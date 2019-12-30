// Maximum period of the deferred transaction is 45 days;

#include <eosio/eosio.hpp>
#include <eosio/print.hpp>
#include <eosio/asset.hpp>
#include <eosio/system.hpp>
#include <eosio/transaction.hpp>

using namespace eosio;

typedef std::function<void(const uint64_t*, const name*, const name*)> notify_func;

class [[eosio::contract("locktimer")]] locktimer : public eosio::contract {
  private:

    const symbol lock_symbol;
    const asset FEE;
    const asset MIN;
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

    };
    typedef eosio::multi_index<"timerv1"_n, timer, indexed_by<"bysender"_n, const_mem_fun<timer, uint64_t, &timer::get_secondary_1>>> timer_index;

    timer_index table;

    uint32_t now() {
      return current_time_point().sec_since_epoch();
    }


  public:
    using contract::contract;
    locktimer(name receiver, name code, datastream<const char *> ds) : contract(receiver, code, ds), lock_symbol("EOS", 4),
    FEE(300, this->lock_symbol), MIN(500, this-> lock_symbol),
    table(_self, _self.value) {}

    [[eosio::on_notify("eosio.token::transfer")]]
    void ontransfer(const name& sender, const name& to, const eosio::asset& quantity, const std::string& memo)
    {
      if (to != get_self() || sender == get_self()) return;
      check(quantity.amount > 0, "When pigs fly");
      check(quantity.symbol == lock_symbol, "These are not the droids you are looking for.");
      if(memo == "createtimer") {
        if(quantity < MIN) print(quantity);
        check(quantity >= MIN, "Minimum amount of deposit is 0.0500 EOS. Be aware that the fee is 0.0300 EOS");
        uint64_t primary_key = table.available_primary_key();
        table.emplace(get_self(), [&](auto &row) {
          row.id = primary_key;
          row.sender = sender;
          row.receiver = sender;
          row.quantity = quantity - FEE;
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
      check(now() < date, "The date is already passed");
      const uint32_t twoyears = 31556926 + 31556926;
      check(date - now() <= twoyears, "Maximum delay supported from now is 2 years");

      auto timer = table.find(id);
      check(timer != table.end(), "Timer with this id doesn't exist");
      check(timer->sender == sender, "You are not the owner of this timer");
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
    void defertxn(const uint32_t& delay, const uint64_t& sendid, const uint64_t& _id) {
        require_auth(get_self());
        eosio::transaction deferred;
        uint32_t max_delay = 3888000; //max delay supported by EOS 3888000
        if (delay <= max_delay){
          deferred.actions.emplace_back (
            permission_level{get_self(), "active"_n},
            get_self(), "autosend"_n,
            std::make_tuple(_id)
          );
          deferred.delay_sec = delay;
          deferred.send(_id, get_self());
        //perform your transaction here
        }
        else{
            uint32_t remaining_delay = delay - max_delay;
            uint64_t newid = updateSenderId(sendid); //sender id should be updated for every recursive call
            // transaction to update the delay
            deferred.actions.emplace_back(
                eosio::permission_level{get_self(), "active"_n},
                get_self(),
                "defertxn"_n,
                std::make_tuple(remaining_delay, newid, _id));
            deferred.delay_sec = max_delay; // here we set the new delay which is maximum until remaining_delay is less the max_delay
            deferred.send(sendid, get_self());
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
        std::make_tuple(delay, id, id)
      ).send();
    }
    uint64_t updateSenderId(const uint64_t& id) {
      const uint64_t base = 10000000;
      if(id < base) return id + base;
      else return id - base;
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
