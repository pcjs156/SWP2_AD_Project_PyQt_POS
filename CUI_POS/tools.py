import sys


# "filename" 이라는 이름의 interface 파일이 존재하면 해당 파일을 불러오고,
# 파일이 존재하지 않으면 파일을 새로 생성한 뒤 개행 문자로 구분되어 strip된 각 행을 요소로 가지는 list를 반환.
def read_interface_file(filename: str, prefix="") -> list:
    from CUI_POS.core import Product

    FILENAME = f"{prefix}DB/{filename}"

    print(f"Loading {FILENAME}...")
    try:
        try:
            f = open(f"{FILENAME}", "r", encoding="utf-8")
            raw_string = f.read().strip()
            interface_lines = list(line.strip() for line in raw_string.split('\n'))
            f.close()

            # 파일이 비어 있는 경우 발생
            if len(interface_lines) == 1 and interface_lines[0] == '':
                raise Product.InterfaceFileIsEmpty

        # 파일이 존재하지 않음
        except FileNotFoundError:
            with open(f"{FILENAME}", 'w') as f:
                print(f"{FILENAME}이 존재하지 않아 새로 생성합니다.")

            with open(f"{FILENAME}", 'r') as f:
                raw_string = f.read().strip()
                interface_lines = list(line.strip() for line in raw_string.split('\n'))

            # 파일이 무조건 비어 있으므로 발생
            raise Product.InterfaceFileIsEmpty

    except Product.InterfaceFileIsEmpty as e:
        print(e)
        sys.exit(1)

    return interface_lines
