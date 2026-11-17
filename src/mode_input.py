import math

from src.judge import judge
from src.mac import mac
from src.perf import print_performance

def read_matrix(name, n=3):
    """한 행씩 입력받아 nxn 숫자 배열을 반환한다."""
    print(f"\n{name}: 각 줄에 숫자 {n}개를 공백으로 구분해 입력하세요.")

    matrix = []

    for row in range(n):
        while True:
            line = input(f"{row + 1}행: ")
            parts = line.split()

            if len(parts) != n:
                print(f"입력 형식 오류: 숫자 {n}개를 입력하세요.")
                continue

            try:
                values = [float(part) for part in parts]
            except ValueError:
                print("입력 형식 오류: 숫자만 입력하세요.")
                continue
            
            if not all(math.isfinite(value) for value in values):
                print("입력 형식 오류: 유한한 숫자를 입력하세요.")
                continue

            matrix.append(values)
            break
    
    return matrix

def run_input_mode():
    print("\n[1] 필터 입력")

    filter_a = read_matrix("필터 A")
    filter_B = read_matrix("필터 B")

    print("\n필터 A, B 저장 완료")

    print("\n[2] 패턴 입력")
    pattern = read_matrix("패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_B)
    verdict = judge(score_a, score_b)

    print("\n[3] MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")

    if verdict == "UNDECIDED":
        print("판정: 판정 불가 (UNDECIDED)")
    else:
        print(f"판정: {verdict}")

    print_performance([
        (3, pattern, filter_a),
    ])