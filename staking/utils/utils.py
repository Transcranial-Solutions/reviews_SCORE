def iscore_to_loop(iscore: int) -> int:
        return iscore // 1000


def floor(number: float, decimals: int):
        number = number * 10 ** (decimals + 1)
        number = number // 10
        return number / 10 ** decimals


def loop_to_rscore(loop: int) -> int:
        return loop * 10**18


def rscore_to_loop(rscore: int) -> int:
        return rscore // 10**18


def compute_rscore_reward_rate(distribution_amount: int, total_review_lockup: int) -> int:
        return loop_to_rscore(distribution_amount) // total_review_lockup