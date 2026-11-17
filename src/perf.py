import time

from src.mac import mac


REPEAT = 10


def measure_mac_ms(pattern, filt, repeat=REPEAT):
    """MAC 함수 호출 시간을 반복 측정해 평균 ms를 반환한다."""
    elapsed = 0.0

    for _ in range(repeat):
        start = time.perf_counter()
        mac(pattern, filt)
        elapsed += time.perf_counter() - start

    return elapsed / repeat * 1000


def print_performance(cases):
    """(크기, 패턴, 필터) 목록을 받아 성능 표를 출력한다."""
    print(f"\n[성능 분석] MAC 1회 기준, {REPEAT}회 평균")
    print(f"{'크기':<10} {'평균 시간(ms)':>15} {'MAC 횟수(N²)':>15}")
    print("-" * 46)

    for n, pattern, filt in cases:
        average_ms = measure_mac_ms(pattern, filt)

        print(
            f"{str(n) + 'x' + str(n):<10} "
            f"{average_ms:>15.6f} "
            f"{n * n:>15}"
        )