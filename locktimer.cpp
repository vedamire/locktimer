// #include <eosio/eosio.hpp>
// #include <eosio/asset.hpp>
// using namespace eosio;
//
// class [[eosio::contract]] locktimer : public contract {
//   private:
//     struct [[eosio::table]] timer
//     {
//       uint64_t id;
//       name sender;
//       name receiver;
//       eosio::asset quantity;
//       bool is_filled;
//       uint32_t start_date;
//       uint32_t end_date;
//       uint64_t primary_key() const { return id; }
//       // uint64_t get_secondary_1() const { return sender.value;}
//     };
//     typedef eosio::multi_index<"timerv1"_n, timer> timer_index; // keep names short
//
//     // typedef eosio::multi_index<"timer_v001"_n, timer_v001, indexed_by<"bysender"_n, const_mem_fun<timer_v001, uint64_t, &timer_v001::get_secondary_1>>> timer_table;
//     timer_index table;
//   public:
//       using contract::contract;
//       locktimer(name receiver, name code, datastream<const char*> ds):contract(receiver, code, ds), table(_self, get_first_receiver().value) {}
//
//       [[eosio::action]]
//       void hi( name user ) {
//          print( "Hello, ", user);
//       }
// };





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
      bool is_filled;
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
    locktimer(name receiver, name code, datastream<const char *> ds) : contract(receiver, code, ds), wage_symbol("EOS", 4), table(_self, _self.value) {}


    [[eosio::on_notify("eosio.token::transfer")]]
    void filltimer(const name& employer, const name& to, const eosio::asset& quantity, const std::string& memo)
    {
      if (to != get_self() || employer == get_self())
      {
        print("These are not the droids you are looking for.");
        return;
      }
      check(quantity.amount > 0, "When pigs fly");
      check(quantity.symbol == wage_symbol, "These are not the droids you are looking for.");
    }

    [[eosio::action]]
    void lockmoney() {

    }

    [[eosio::action]]
    void claimmoney() {

    }
};
