from iconservice import *

class RewardHandler:
    """
    Handles distribution and reward tracking. Used within the contract that keeps track of eligible balances.
    """

    def __init__(self, name: str, db: IconScoreDatabase, isb: IconScoreBase, rscore_decimals: int = 18):
        """
        Initialization

        Parameters:
        name            :  Name to differentiate between databases if several rewardhandlers are used in the same contract.
        db              :  Database instance used to store persistent data.
        isb             :  Contract instance of the contract this class is used in.
        rscore_decimals :  Specifies how small unit rewards should be measured in.
        token_type      :  Specifies which type of token the rewards are in.
        """
        self._reward_rate = VarDB(f"{name}_sum_reward_rate", db, int)
        self._entry_reward_rate = DictDB(f"{name}_entry_reward_rate", db, int)
        self._rewards = DictDB(f"{name}_rewards", db, int)
        self._rscore_decimals = rscore_decimals
        self._isb = isb

    def distribute_rewards(self, amount: int, total_eligible_supply: int):
        """
        Trigger a reward distribution.

        Parameters:
        amount                 :  Amount of tokens to distribute.
        total_eligible_supply  :  Total amount of tokens eligible for rewards.
        """
        reward_rate = self._reward_rate.get()
        if total_eligible_supply:
            reward_rate = reward_rate + (self._loop_to_rscore(amount) // total_eligible_supply)
            self._reward_rate.set(reward_rate)
        else:
            revert("Total supply is zero.")

    # Add mint/transfer argument?
    def claim_rewards(self, address: Address, eligible_balance: int) -> int:
        """
        Computes all rewards the user has accumulated These rewards are deducted from the reward tracker.
        Returns the accumulated rewards. It's up to the imlpementer to implement the way these rewards end up 
        with the end user. E.g. mint or transfer.

        Parameters:
        address  :  Address which will claim the rewards.
        eligible_balance  :  Number of tokens, at this point in time, the address has that are eligible for rewards.
        """
        self.update_rewards(address, eligible_balance)

        rewards = self._rscore_to_loop(self._rewards[address])
        if not rewards:
            revert("No rewards to claim.")

        self._rewards[address] -= self._loop_to_rscore(rewards)
        return rewards

    def query_rewards(self, address: Address, eligible_balance: int) -> int:
        """
        Query the rewards avaiable for this address to claim.

        Parameters:
        address           :  Address to query rewards for.
        eligible_balance  :  Number of tokens, at this point in time, the address has that are eligible for rewards.
        """
        rewards = eligible_balance * (self._reward_rate.get() - self._entry_reward_rate[address]) + self._rewards[address]
        return self._rscore_to_loop(rewards)

    def update_rewards(self, address: Address, eligible_balance: int):
        """
        Computes all rewards up to this point in time and records them. Next, the entry reward is updated to the current
        reward rate. ALWAYS use this method before changing the eligible balance of an address (for example before
        staking and unstaking in the irc2 contract) If this is not done the reward tracking will not be accurate.

        Parameters
        address           :  Address to update rewards on.
        eligible_balance  :  Number of tokens, at this point in time, the address has that are eligible for rewards.
        """
        rewards = eligible_balance * (self._reward_rate.get() - self._entry_reward_rate[address])
        self._rewards[address] += rewards
        self._entry_reward_rate[address] = self._reward_rate.get()

    def _rscore_to_loop(self, rscore: int) -> int:
        """
        Convert rscore to loop. 
        """
        return rscore // 10**self._rscore_decimals

    def _loop_to_rscore(self, loop: int) -> int:
        """
        Convert loop to rscore.
        """
        return loop * 10**self._rscore_decimals