def icx_to_loop(icx: float) -> int:
    """
    Convert Icx to loop.
    """
    return int(icx * 10 ** 18)


def loop_to_icx(loop: int) -> float:
    """
    Convert loop to icx.
    """
    return loop / (10 ** 18)
