import sys
import pickle

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


# 제품 개별 판매 정보
class ProductSalesData:
    def __init__(self, product_code: int):
        # 제품별 고유 코드
        self.product_code = product_code
        # 제품 판매 개수
        self.sales_count = 0
        # 제품 총 판매액
        self.sales_total = 0

class POSCore:
    def __init__(self):
        self.product_datas = None

        try:
            # 제품 정보 Interface 파일 로딩
            product_info_lines = read_interface_file(Product.PRODUCT_INTERFACE_FILENAME)
            if len(product_info_lines) == 0:
                raise Product.InterfaceFileIsEmpty

            # 제품 정보 data 파일을 dictionary로 변환
            self.product_datas = {pair[0]: pair[1] for pair in map(Product.get_code_product_pair, product_info_lines)}

            # 제품별 판매 정보(product_sales_data)를 불러옴

        except Product.InterfaceFileIsEmpty as e:
            print(e)
            sys.exit(1)

    def run(self):
        print("POS is starting...")
