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
    const symbol wage_symbol;
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
    locktimer(name receiver, name code, datastream<const char *> ds) : contract(receiver, code, ds), wage_symbol("SYS", 4), table(_self, _self.value) {}


    [[eosio::on_notify("eosio.token::transfer")]]
    void listener(const name& sender, const name& to, const eosio::asset& quantity, const std::string& memo)
    {
      if (to != get_self() || sender == get_self()) return;
      check(quantity.amount > 0, "When pigs fly");
      check(quantity.symbol == wage_symbol, "These are not the droids you are looking for.");
      if(memo == "createtimer") {
        uint64_t primary_key = table.available_primary_key();
        table.emplace(get_self(), [&](auto &row) {
          row.id = primary_key;
          row.sender = sender;
          row.receiver = _self;
          row.quantity = quantity;
          row.is_sent = false;
          row.start_date = NULL;
          row.end_date = NULL;
        });
      } else if(memo == "replenish") {
        print("Account is successfully replenished");
      } else {
        check(false, "Wrong memo. To transfer money here use ether 'createtimer' or 'replenish' memo");
      }
    }

    [[eosio::action]]
    void lock(const name& sender, const name& receiver, const uint64_t& id, const uint32_t& date) {
      require_auth(sender);
      check(is_account(receiver), "Receiver's account doesn't exist");
      check(now() < date, "The date is already passed");
      check(date - now() <= 3888000, "Maximum delay supported from now is 45 days");

      auto timer = table.find(id);
      check(timer != table.end(), "Timer with this id doesn't exist");
      check(timer->sender == sender, "You are not the owner of this timer");
      table.modify(timer, get_self(), [&](auto& row) {
        row.receiver = receiver;
        row.start_date = now();
        row.end_date = date;
        row.is_sent = true;
      });
      // Send deferred;
      eosio::transaction deferred;

      deferred.actions.emplace_back (
        permission_level{get_self(), "active"_n},
        get_self(), "autosend"_n,
        std::make_tuple(id)
      );
      deferred.delay_sec = timer->end_date - now();
      deferred.send(id, get_self());
    }

    [[eosio::action]]
    void autosend(const uint64_t& id) {
      require_auth(get_self());
      auto timer = table.find(id);
      check(timer != table.end(), "There's no wage contract with such an id");
      check(timer->is_sent == true, "The transaction isn't sent yet");
      check(timer->end_date - 1 < now(), "Time isn't passed yet");
      // auto wage = table_wage.find(id);
      action{
        permission_level{get_self(), "active"_n},
        "eosio.token"_n,
        "transfer"_n,
        std::make_tuple(get_self(), timer->receiver, timer->quantity, std::string("Locked money are released!"))
      }.send();
      table.erase(timer);


      // check(wage != table_wage.end(), "There's no wage contract with such an id");
      // check(wage->is_accepted == true, "The wage contract isn't accepted");

      // cash_out_transaction(wage, table_wage);
    }

    [[eosio::action]]
    void cancel(const name& sender, const uint64_t& id) {
      require_auth(sender);
      auto timer = table.find(id);
      check(timer != table.end(), "Timer with this id doesn't exist");
      check(timer->sender == sender, "You are not the owner of this timer");
      check(timer->is_sent == false, "Money are already locked and can't be unlocked until the date");
      table.erase(timer);
    }

    [[eosio::action]]
    void claimmoney(const name& receiver, const uint64_t& id) {
      require_auth(receiver);
      auto timer = table.find(id);
      check(timer != table.end(), "Timer with this id doesn't exist");
      check(timer->is_sent == true, "Money aren't sent yet");
      check(timer->receiver == receiver, "You are not the receiver of this timer");
      check(timer->end_date - 1 < now(), "Time isn't passed yet");

      action{
        permission_level{get_self(), "active"_n},
        "eosio.token"_n,
        "transfer"_n,
        std::make_tuple(get_self(), timer->receiver, timer->quantity, std::string("Locked money are released!"))
      }.send();
      table.erase(timer);
    }

    [[eosio::action]]
    void ping(const name& name) {
      require_auth(name);
      print("Contract is working");
    }
};
