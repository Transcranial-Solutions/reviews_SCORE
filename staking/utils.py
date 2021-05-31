
def iscore_to_loop(iscore: int) -> int:
        return iscore // 1000

def floor(number: float, decimals: int):
        number = number * 10 ** (decimals + 1)
        number = number // 10
        return number / 10 ** decimals