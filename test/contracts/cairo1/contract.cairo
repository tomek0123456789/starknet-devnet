#[contract]
mod Contract {
    struct Storage {
        balance: felt,
    }

    #[constructor]
    fn constructor(initial_balance: felt) {
        balance::write(initial_balance);
    }

    #[external]
    fn increase_balance(amount1: felt, amount2: felt) {
        balance::write(balance::read() + amount1 + amount2);
    }

    #[view]
    fn get_balance() -> felt {
        balance::read()
    }
}