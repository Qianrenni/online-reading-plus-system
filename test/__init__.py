import time
import math


def manual_factorial(n):
    """手动实现阶乘"""
    if n < 0:
        raise ValueError("负数没有阶乘")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def test_factorial_performance():
    test_values = [10, 50, 100, 200, 500]

    print(f"{'n':<6} {'math.factorial()':<18} {'manual_factorial()':<18} {'Ratio':<8}")
    print("-" * 55)

    for n in test_values:
        # 官方实现
        start = time.perf_counter()
        result1 = math.factorial(n)
        time1 = time.perf_counter() - start

        # 手动实现
        start = time.perf_counter()
        result2 = manual_factorial(n)
        time2 = time.perf_counter() - start

        ratio = time2 / time1 if time1 > 0 else float('inf')
        equal = "✓" if result1 == result2 else "✗"

        print(f"{n:<6} {time1:<18.6f} {time2:<18.6f} {ratio:<8.2f} {equal}")


test_factorial_performance()