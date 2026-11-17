EPSILON = 1e-9

def judge(score_a, score_b, label_a="A", label_b="B"):
    """두 점수의 차이가 허용오차보다 작으면 동점으로 처리한다."""
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    if score_a > score_b:
        return label_a

    return label_b

def normalize_label(raw):
    """원본 라벨을 Cross 또는 X로 통일한다."""
    if not isinstance(raw, str):
        return None

    label = raw.strip().lower()

    if label in ("+", "cross"):
        return "Cross"

    if label == "x":
        return "X"

    return None