import re

# 정수에 1000 단위로 콤마를 넣어줌
def number_with_comma(val):
    return re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1,", "%d" % val)

# 콤마가 포함된 정수 문자열에서 콤마를 없애고 정수로 변환해줌
def delete_comma(val: str) -> int:
    val = val.strip()

    while ',' in val:
        idx = val.find(",")
        val = val[:idx] + val[idx+1:]

    return int(val)
