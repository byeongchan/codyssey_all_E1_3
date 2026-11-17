def mac(pattern, filt):
    """같은 위치의 값을 곱하고 모두 더한다."""
    total = 0
    n = len(pattern)

    for row in range(n):
        for col in range(n):
            total += pattern[row][col] * filt[row][col]
    
    return total