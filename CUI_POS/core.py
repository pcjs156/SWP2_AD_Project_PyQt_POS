import sys
from datetime import datetime

from CUI_POS.tools import read_interface_file


# 제품 개별 정보 데이터
class Product:
    DELIMITER = ','
    COLUMN_LEN = 3

    PRODUCT_INTERFACE_FILENAME = "product_interface"
    PRODUCT_DATA_FILENAME = "product_datas"

    def __init__(self, name: str, price: int, discount_rate: int):
        self.name = name
        self.price = price
        self.discount_rate = discount_rate

    # (제품 코드:Product 클래스) 쌍의 tuple을 반환
    @staticmethod
    def get_code_product_pair(line: str) -> tuple:
        from CUI_POS.core import Product

        error_occured = True

        try:
            # Product.DELIMITER를 기준으로 문자열을 분리
            tokens = list(word.strip() for word in line.split(Product.DELIMITER))
            # 정의된 Column 길이와 현재 row의 column 길이가 다른 경우
            if len(tokens) != Product.COLUMN_LEN:
                raise Product.InconsistentColumnLength

            name, price, discount_rate = tokens[0], int(tokens[1]), int(tokens[2])

            # 유효한 할인율이 아닌 경우
            if not (0 <= discount_rate <= 100):
                raise Product.InvalidDiscountRate
            # 가격이 0 미만의 값인 경우
            if price < 0:
                raise Product.NegativePrice

        except (Product.InvalidDiscountRate, Product.NegativePrice, Product.InconsistentColumnLength) as e:
            print(e)

        # 형 변환이 불가능한 값이 입력된 경우
        except ValueError:
            print("형 변환이 불가능한 값이 입력되었습니다.")

        else:
            # 에러가 발생하지 않았음을 표시
            error_occured = False

        finally:
            if error_occured:
                print(f"ERROR: {line}")
                sys.exit(1)
            else:
                return name, Product(name, price, discount_rate)

    # 입력된 수량 만큼의 제품 가격을 계산
    def calc_price(self, quantity):
        return int(self.price * quantity * (100 - self.discount_rate) / 100)

    # DB/product_interface 파일이 비어 있는 경우 발생
    class InterfaceFileIsEmpty(Exception):
        def __str__(self):
            return "DB/product_interface 파일이 비어 있습니다."

    # Product column의 길이가 Product.COLUMN과 다른 경우 발생
    class InconsistentColumnLength(Exception):
        def __str__(self):
            return "Column의 크기가 잘못된 Row가 존재합니다."

    # price가 0 미만의 값일 때 발생
    class NegativePrice(Exception):
        def __str__(self):
            return "제품 가격이 0 미만의 값입니다."

    # discount_rate가 0 미만 100 초과의 값일 때 발생
    class InvalidDiscountRate(Exception):
        def __str__(self):
            return "유효하지 않은 할인율입니다(0 미만, 100 초과의 값입니다)."


# POSCore 클래스에 하나씩 존재하는 매출 정보 저장/처리 클래스
class TotalSales:
    def __init__(self):
        self.sales_list = list()

    def record(self, sales):
        # 결제 단위로 판매 정보(ProductSalesData)를 [판매시각, 판매정보들] list로 저장하는 list
        now = datetime.now()
        sales_datetime_info = f"{now.year}년 {now.month}월 {now.day}일 {now.hour}시 {now.minute}분 {now.second}초"
        self.sales_list.append((sales_datetime_info, sales))


class POSCore:
    COMMAND_CODES = {0: "종료", 1: "판매", 2: "매출 정보 확인"}

    def __init__(self):
        # POS기 구동 시작 시각
        self.RUNNING_START_TIME = datetime.now()
        # 상품 정보(상품명: Product class) dictionary
        self.product_datas = None

        try:
            # 제품 정보 Interface 파일 로딩
            product_info_lines = read_interface_file(Product.PRODUCT_INTERFACE_FILENAME)
            if len(product_info_lines) == 0:
                raise Product.InterfaceFileIsEmpty

            # 제품 정보 data 파일을 dictionary로 변환
            self.product_datas = {pair[0]: pair[1] for pair in map(Product.get_code_product_pair, product_info_lines)}

            # 프로그램 종료시까지 갱신할 제품 판매 정보를 기록 (제품명:판매정보 pair)
            self.total_sales_info = TotalSales()

        except Product.InterfaceFileIsEmpty as e:
            print(e)
            sys.exit(1)

    def run(self):
        print("POS is running now.")
        while True:
            # POS기 조작 명령을 받음
            command = self.get_command()
            # 코드 0: 종료
            if command == 0:
                self.write_sales_record()
                print("POS를 종료합니다.")
                sys.exit(0)
            # 코드 1: 제품 판매(계산)
            elif command == 1:
                self.sell_products()
            elif command == 2:
                header = ""
                start_time = self.RUNNING_START_TIME
                header += "[POS 시작 시간]\n"
                header += f"{start_time.year}년 {start_time.month}월 {start_time.day}일 {start_time.hour}시 {start_time.minute}분 {start_time.second}초\n"
                header += '=' * 70 + '\n'

                print(self.get_sales_record_string(header))

    # POS기 조작 명령을 받음
    def get_command(self):
        # 올바른 입력을 받을 때까지 반복
        while True:
            print("\n수행할 명령을 입력해 주세요.")
            for code, command in POSCore.COMMAND_CODES.items():
                print(f"{code} : {command}")

            try:
                command = int(input(">>> "))
                if command not in POSCore.COMMAND_CODES.keys():
                    print("유효한 명령을 입력해 주세요.")
                else:
                    break

            except ValueError:
                print("정수로 변환 가능한 값을 입력해 주세요.")

        return command

    # 제품 판매
    def sell_products(self):
        print("제품을 판매합니다.")
        print("\"계산\"을 입력하시면 해당 명령 입력 시점 전까지의 제품들이 계산됩니다.")
        print("\"취소\"를 입력하시면 제품 판매를 취소합니다.")
        print("제품명을 입력하시면 판매 개수를 추가적으로 입력받아 해당 제품을 계산 목록에 추가합니다.")

        print("메뉴 " + "=" * 50)
        for product in self.product_datas.values():
            print(f"{product.name} : {product.price}원 -> {product.calc_price(1)}원 ({product.discount_rate}% 세일)")

        sales_record = dict()

        while True:
            total_price = 0
            print(f"\n현재 목록에 담긴 제품: {sum(sales_record.values())}개")
            for product_name, quantity in sales_record.items():
                print(f"{product_name} {quantity}개: {self.product_datas[product_name].calc_price(quantity)}원")
                total_price += self.product_datas[product_name].calc_price(quantity)
            print(f"총 {total_price}원")

            order = input("상품명: ")
            if order == "취소":
                print("결제를 취소합니다.")
                return

            elif order == "계산":
                # 입력된 판매 정보가 없을 때
                if len(sales_record) == 0:
                    print("입력된 판매 정보가 없습니다. 결제를 취소합니다.")
                    return
                else:
                    print("=" * 70)
                    tot = 0
                    for record in sales_record:
                        print(f"{record} {sales_record[record]}개 : {self.product_datas[record].calc_price(sales_record[record])}원")
                        tot += self.product_datas[record].calc_price(sales_record[record])
                    print(f"합계: {tot}원\n")
                    self.total_sales_info.record([{"품목": record,
                                                   "갯수": sales_record[record],
                                                   "판매액": self.product_datas[record].calc_price(sales_record[record])}
                                                  for record in sales_record.keys()])
                    return

            # 판매중인 제품인 경우
            elif order in self.product_datas.keys():
                # 만약 판매중인 상품이면
                if order in self.product_datas.keys():
                    try:
                        quantity = int(input("몇 개? : "))
                        # 수량이 0으로 입력된 경우
                        if quantity == 0:
                            raise ValueError
                    except ValueError:
                        print("갯수는 0이 아닌 정수로 입력되어야 합니다.")

                    else:
                        # 현재 장바구니에 해당 제품이 있는 경우
                        if order in sales_record.keys():
                            # 양을 추가해줌
                            if quantity > 0:
                                sales_record[order] += quantity
                            # quantity가 음수인 경우, 해당 수만큼 수량을 빼줌
                            else:
                                # 만약 빼려는 양이 현재 양보다 큰 경우
                                if (sales_record[order] + quantity) < 0:
                                    print(f"{order} 제품은 {sales_record[order]}개보다 많이 뺄 수 없습니다.")
                                # 만약 현재 수량과 같게 제품 수량을 빼는 경우
                                elif (sales_record[order] + quantity) == 0:
                                    # 해당 제품을 계산 목록에서 삭제
                                    del sales_record[order]
                                # 정상적으로 해당 수량만큼 빼주는 경우
                                else:
                                    sales_record[order] += quantity

                        # 현재 장바구니에 해당 제품이 없는 경우
                        else:
                            if quantity < 0:
                                print("제품 수량은 0보다 작을 수 없습니다.")
                            else:
                                sales_record[order] = quantity

                else:
                    print("판매중인 제품이 아닙니다.")

            # 알 수 없는 입력인 경우
            else:
                print("알 수 없는 입력입니다.")

    # 매출 정보를 string으로 받아옴
    def get_sales_record_string(self, header: str):
        ret = header
        tot = 0

        for record in self.total_sales_info.sales_list:
            ret += record[0] + '\n'
            for sell_info in record[1]:
                ret += f"{sell_info['품목']} {sell_info['갯수']}개 : {sell_info['판매액']}\n"
                tot += sell_info['판매액']

            ret += "\n"
            ret += f"합계: {tot}원\n"
            ret += '-' * 70 + '\n'

        ret += "=" * 70
        return ret

    def write_sales_record(self):
        header = ""
        start_time = self.RUNNING_START_TIME
        header += "[POS 시작 시각]\n"
        header += f"{start_time.year}년 {start_time.month}월 {start_time.day}일 {start_time.hour}시 {start_time.minute}분 {start_time.second}초\n"

        header += "[POS 종료 시각]\n"
        end_time = datetime.now()
        formatted_end_time = f"{end_time.year}년 {end_time.month}월 {end_time.day}일 {end_time.hour}시 {end_time.minute}분 {end_time.second}초"
        header += formatted_end_time + '\n'
        header += '=' * 70 + '\n'

        content = self.get_sales_record_string(header)

        with open(f"sales/{formatted_end_time}.txt", 'w', encoding="utf-8") as f:
            f.write(content)