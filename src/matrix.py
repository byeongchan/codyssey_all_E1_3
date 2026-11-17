def make_matrix(n, fill=0):
    """nxn 크기의 2차원 리스트를 생성한다."""
    if n <= 0:
        raise ValueError("크기는 1 이상이어야 합니다.")

    return [[fill for _ in range(n)] for _ in range(n)]

def make_cross(n):
    """홀수 크기의 십자가 패턴을 생성한다."""
    if n <= 0 or n % 2 == 0:
        raise ValueError("크기는 양의 홀수여야 합니다.")

    matrix = make_matrix(n)
    center = n // 2

    for i in range(n):
        matrix[center][i] = 1
        matrix[i][center] = 1

    return matrix