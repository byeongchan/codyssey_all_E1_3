import json
import math
import re
from pathlib import Path

from src.judge import judge, normalize_label
from src.mac import mac
from src.matrix import make_cross
from src.perf import print_performance

DATA_PATH = Path(__file__).resolve().parent.parent / "data.json"


def validate_matrix(matrix, n, name):
    """배열의 크기와 각 칸의 숫자 값을 검사한다."""
    if not isinstance(matrix, list) or len(matrix) != n:
        raise ValueError(f"{name}: 행 수가 {n}이어야 합니다.")

    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError(f"{name}: 각 행의 열 수가 {n}이어야 합니다.")

        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name}: 숫자가 아닌 값이 있습니다.")

            if not math.isfinite(value):
                raise ValueError(f"{name}: 유한한 숫자만 허용됩니다.")


def load_data(path):
    """JSON 파일을 읽고 최상위 구조를 검사한다."""
    try:
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
    except OSError as error:
        print(f"파일 읽기 오류: {error}")
        return None
    except (json.JSONDecodeError, UnicodeError) as error:
        print(f"JSON 읽기 오류: {error}")
        return None

    if not isinstance(data, dict):
        print("데이터 오류: 최상위 데이터는 객체여야 합니다.")
        return None

    if not isinstance(data.get("filters"), dict):
        print("데이터 오류: filters 객체가 필요합니다.")
        return None

    if not isinstance(data.get("patterns"), dict):
        print("데이터 오류: patterns 객체가 필요합니다.")
        return None

    return data


def prepare_filters(raw_filters):
    """크기별 필터를 검증하고 라벨을 정규화한다."""
    filters = {}
    errors = {}

    for n in (5, 13, 25):
        key = f"size_{n}"

        try:
            group = raw_filters.get(key)

            if not isinstance(group, dict):
                raise ValueError(f"{key} 필터 객체가 없습니다.")

            normalized = {}

            for raw_label, matrix in group.items():
                label = normalize_label(raw_label)

                if label is None:
                    raise ValueError(f"알 수 없는 필터 라벨: {raw_label}")

                if label in normalized:
                    raise ValueError(f"중복된 필터 라벨: {label}")

                validate_matrix(matrix, n, f"{key}/{label}")
                normalized[label] = matrix

            if set(normalized) != {"Cross", "X"}:
                raise ValueError("Cross와 X 필터가 모두 필요합니다.")

            filters[n] = normalized
            print(f"{key}: 필터 로드 완료 (Cross, X)")

        except ValueError as error:
            errors[n] = str(error)
            print(f"{key}: 필터 오류 - {error}")

    return filters, errors


def run_case(case_id, case, filters, filter_errors):
    """한 케이스를 처리하고, 오류도 FAIL 결과로 반환한다."""
    result = {
        "id": case_id,
        "status": "FAIL",
        "reason": "",
        "category": "",
    }

    try:
        match = re.fullmatch(r"size_([1-9]\d*)_([1-9]\d*)", case_id)

        if match is None:
            raise ValueError("케이스 키는 size_N_idx 형식이어야 합니다.")

        n = int(match.group(1))

        if n not in (5, 13, 25):
            raise ValueError(f"지원하지 않는 크기: {n}")

        if n in filter_errors:
            raise ValueError(f"필터 오류: {filter_errors[n]}")

        if not isinstance(case, dict):
            raise ValueError("케이스 데이터는 객체여야 합니다.")

        pattern = case.get("input")
        validate_matrix(pattern, n, "패턴")

        expected = normalize_label(case.get("expected"))

        if expected is None:
            raise ValueError("expected 라벨을 해석할 수 없습니다.")

        score_cross = mac(pattern, filters[n]["Cross"])
        score_x = mac(pattern, filters[n]["X"])

        if not math.isfinite(score_cross) or not math.isfinite(score_x):
            raise ValueError("MAC 결과가 유한한 숫자가 아닙니다.")

        verdict = judge(score_cross, score_x, "Cross", "X")

        result.update({
            "score_cross": score_cross,
            "score_x": score_x,
            "verdict": verdict,
            "expected": expected,
        })

        if verdict == expected:
            result["status"] = "PASS"

        elif verdict == "UNDECIDED":
            result["category"] = "수치 비교"
            result["reason"] = "허용오차 기준 동점(UNDECIDED)"

        else:
            result["category"] = "판정 불일치"
            result["reason"] = (
                f"판정 불일치: expected={expected}, 실제={verdict}"
            )

    except ValueError as error:
        result["category"] = "데이터/스키마"
        result["reason"] = str(error)

    except OverflowError as error:
        result["category"] = "수치 계산"
        result["reason"] = str(error)

    return result


def print_case(result):
    print(f"\n--- {result['id']} ---")

    if "verdict" in result:
        print(f"Cross 점수: {result['score_cross']}")
        print(f"X 점수: {result['score_x']}")
        print(
            f"판정: {result['verdict']} | "
            f"expected: {result['expected']} | "
            f"{result['status']}"
        )
    else:
        print("FAIL")

    if result["reason"]:
        print(f"사유: {result['reason']}")


def print_summary(results):
    failures = [
        result for result in results
        if result["status"] == "FAIL"
    ]

    print("\n[결과 요약]")
    print(f"전체: {len(results)}")
    print(f"통과: {len(results) - len(failures)}")
    print(f"실패: {len(failures)}")

    if not failures:
        print("실패 케이스 없음")
        return

    print("\n실패 케이스:")
    categories = {}

    for result in failures:
        category = result["category"]

        print(
            f"- {result['id']}: "
            f"[{category}] {result['reason']}"
        )

        categories[category] = categories.get(category, 0) + 1

    print("\n실패 분류:")

    for category, count in categories.items():
        print(f"- {category}: {count}건")


def run_json_mode():
    data = load_data(DATA_PATH)

    if data is None:
        return

    print("\n[1] 필터 로드")
    filters, filter_errors = prepare_filters(data["filters"])

    print("\n[2] 패턴 분석")
    results = []

    for case_id, case in data["patterns"].items():
        result = run_case(case_id, case, filters, filter_errors)
        results.append(result)
        print_case(result)

    cross_3 = make_cross(3)
    performance_cases = [
        (3, cross_3, cross_3),
    ]

    for n in (5, 13, 25):
        if n in filters:
            pattern = make_cross(n)
            filt = filters[n]["Cross"]
            performance_cases.append((n, pattern, filt))
        else:
            print(f"\n{n}x{n}: 필터 오류로 성능 측정을 건너뜁니다.")

    print_performance(performance_cases)
    print_summary(results)