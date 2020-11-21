import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QCoreApplication

from CUI_POS.tools import read_interface_file
from CUI_POS.core import Product, TotalSales

from collections import Counter

class CustomButton(QPushButton):
    def __init__(self, button_text, callback):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setText(button_text)
        self.clicked.connect(callback)

class ProductButton(CustomButton):
    def __init__(self, POS, button_text, callback=lambda x: x):
        super().__init__(button_text, callback)
        self.POS = POS

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.POS.purchase(self.text(), 1)
        elif QMouseEvent.button() == Qt.RightButton:
            self.POS.remove_product(self.text(), 1)


class GUIPosWindow(QWidget):
    SEPARATOR_LENGTH = 70

    def __init__(self):
        super().__init__()

        # 파일 불러오기
        product_info_lines = read_interface_file(Product.PRODUCT_INTERFACE_FILENAME)
        if len(product_info_lines) == 0:
            raise Product.InterfaceFileIsEmpty
        # 제품 이름: 제품 객체(Product)
        self.product_datas = {pair[0]: pair[1] for pair in map(Product.get_code_product_pair, product_info_lines)}

        # 구매한 제품의 목록을 제품 이름(name), 구매 갯수(quantity), 제품 객체(object)를 키로 가지는 dict로 저장
        self.purchasing_list = list()

        self.initUI()

        # POS가 구동되기 시작한 날짜/시각을 저장
        now = datetime.now()
        self.sales_datetime_info = f"{now.year}년 {now.month}월 {now.day}일 {now.hour}시 {now.minute}분 {now.second}초"

        # POS 시작부터 확인 시점까지의 총 매출
        self.total_profit = 0
        # POS 시작부터 확인 시점까지의 총 할인액
        self.total_discountprice = 0
        # 매출 기록 파일 생성

        self.dict1={}
        self.create_record_file()

    def initUI(self):
        # upperlayout- left
        self.purchasing_list_widget = QTableWidget(30, 5)
        self.purchasing_list_widget.setHorizontalHeaderLabels(["제품명", "단가", "할인", "수량", "합계"])
        self.purchasing_list_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.purchasing_list_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.purchasing_list_widget.resizeColumnsToContents()
        self.purchasing_list_widget.resizeRowsToContents()
        self.purchasing_list_widget.setMinimumSize(550, 500)

        # lowerlayout - left
        self.total_price_widget = QTableWidget(4, 1)
        self.total_price_widget.setVerticalHeaderLabels(["주문 금액", "할인 금액", "청구 금액","받은 금액"])
        self.total_price_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.total_price_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.total_price_widget.horizontalHeader().setVisible(False)
        self.total_price_widget.resizeColumnsToContents()
        self.total_price_widget.resizeRowsToContents()
        self.total_price_widget.setMinimumSize(500, 100)

        # upperlayout - right
        self.menuBox = QGroupBox("메뉴")
        self.menuBox.setToolTip(f"<p><span style='color: blue;'>좌클릭시 제품을 구매 목록에 하나 추가하고,<br></span>"
                              + f"<span style='color: red;'>우클릭시 제품을 구매 목록에서 하나 뺍니다.</span></p>")
        self.upperRightLayOut = QGridLayout()

        r, c = 3, 5
        __tmp_product_pairs = tuple((name, obj) for name, obj in self.product_datas.items())
        for i in range(len(__tmp_product_pairs)):
            product_name, product_obj = __tmp_product_pairs[i]
            product_btn = ProductButton(self, product_name)
            #버튼 폭 최소 길이 고정
            product_btn.setMinimumWidth(120)
            product_btn.setToolTip(f"정가: {product_obj.price}원<br>"
                                   f"할인율: {product_obj.discount_rate}%<br>"
                                   f"가격: {product_obj.calc_price(1)}원")

            self.upperRightLayOut.addWidget(product_btn, i//c, i%c)

        self.menuBox.setLayout(self.upperRightLayOut)

        # lowerlayout - right
        self.paymentbox = QGroupBox("결제방법")
        self.paymentLayout = QVBoxLayout()
        self.cash_button = CustomButton("현금결제", self.buttonClicked)
        self.cash_button.setToolTip( f"<span style='color: red;'>받은 현금을 입력하여 주세요.</span></p>")

        self.card_button = CustomButton("카드결제", self.buttonClicked)
        self.paymentLayout.addWidget(self.cash_button)
        self.paymentLayout.addWidget(self.card_button)
        self.paymentbox.setLayout(self.paymentLayout)

        self.cancel_button = CustomButton("취소", self.buttonClicked)
        self.sales_button = CustomButton("매출 정보", self.buttonClicked)
        self.gain_button = CustomButton("총 매출량", self.buttonClicked)

        self.function_layout = QHBoxLayout()
        self.function_layout.addWidget(self.paymentbox)
        self.function_layout.addWidget(self.cancel_button)
        self.function_layout.addWidget(self.sales_button)
        self.function_layout.addWidget(self.gain_button)

        # layout
        self.upper_layOut = QHBoxLayout()
        self.upper_layOut.addWidget(self.purchasing_list_widget)
        self.upper_layOut.addWidget(self.menuBox)

        self.lower_layOut = QHBoxLayout()
        self.lower_layOut.addWidget(self.total_price_widget)
        self.lower_layOut.addLayout(self.function_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.upper_layOut)
        self.main_layout.addLayout(self.lower_layOut)

        self.setLayout(self.main_layout)
        self.setWindowTitle('AD PROJECT')

    def buttonClicked(self):
        button = self.sender()
        key = button.text()

        # 계산 버튼을 누른 경우
        if key == "현금결제":
            # 아무 것도 없는데 계산을 시도할 경우
            if len(self.purchasing_list) == 0:
                QMessageBox.information(
                    self, "ERROR!", "구매 목록이 비어 있습니다."
                )
            elif not self.total_price_widget.item(3, 0):
                QMessageBox.information(
                    self, "ERROR!", "받은 금액을 입력하세요."
                )
            else:
                try:
                    # 총액보다 현금을 덜 받았는지 검사
                    received_money = int(self.total_price_widget.item(3, 0).text())
                    total_price = int(self.total_price_widget.item(2, 0).text())
                    if received_money < total_price:
                        QMessageBox.information(
                            self, "ERROR!", "현금이 부족합니다."
                        )

                    else:
                        self.cash_pay()
                except ValueError:
                    QMessageBox.information(
                        self, "ERROR!", "정수로 변환 가능한 값을 입력해 주세요."
                    )

        elif key == "카드결제":
            # 아무 것도 없는데 계산을 시도할 경우
            if len(self.purchasing_list) == 0:
                QMessageBox.information(
                    self, "ERROR!", "구매 목록이 비어 있습니다."
                )
            else:
                self.card_pay()

        # 취소 버튼을 누른 경우
        elif key == "취소":
            if len(self.purchasing_list) == 0:
                QMessageBox.information(
                    self, "ERROR!", "구매 목록이 비어 있습니다."
                )
            else:
                self.purchasing_list.clear()
                self.clear_screen()

        # 매출 정보 버튼을 누른 경우
        elif key == "매출 정보":
            # if len(self.purchasing_list) == 0:
            #     QMessageBox.information(
            #         self, "ERROR!", "구매 목록이 비어 있습니다."
            #     )
            # else:
                self.read_sales()

        elif key == "총 매출량":
            self.total_sales()
        else:
            print("알 수 없는 버튼입니다.")
            sys.exit(-1)

    def total_sales(self):
        # self.dict = sorted(self.dict.items(),reverse=True, key = lambda x:x[1])
        # result_sales=""
        # for i in self.dict[:3]:
        #     result_sales+=i
        result_sales = ""

        ab = self.dict1.most_common(1)
        b = dict(ab)
        for i in b:
            result_sales+=i

        QMessageBox.information(
            self, "결제 완료", result_sales
        )

    # product_name이라는 이름의 제품을 quantity만큼 구매
    def purchase(self, product_name: str, quantity: int):
        # 만약 구매 목록에 있는 상품인 경우
        if product_name in list(map(lambda p: p["name"], self.purchasing_list)):
            # 해당 제품이 저장된 row를 탐색
            row_idx = 0
            while self.purchasing_list[row_idx]["name"] != product_name:
                row_idx += 1

            # 해당 제품의 구매 수량을 quantity만큼 늘려줌
            self.purchasing_list[row_idx]["quantity"] += quantity

        # 만약 구매 목록에 없는 상품인 경우
        else:
            # 새로 추가해줌
            self.purchasing_list.append({"name": product_name,
                                         "quantity": quantity,
                                         "object": self.product_datas[product_name]})
        # 화면 갱신
        self.update_screen()

    # product_name이라는 이름의 제품을 quantity만큼 구매 목록에서 뺌
    def remove_product(self, product_name: str, quantity: int):
        # 만약 구매 목록에 있는 상품인 경우
        if product_name in list(map(lambda p: p["name"], self.purchasing_list)):
            # 해당 제품이 저장된 row를 탐색
            row_idx = 0
            while self.purchasing_list[row_idx]["name"] != product_name:
                row_idx += 1

            # 만약 quantity 이상 많이 구매 목록에 들어있다면
            if self.purchasing_list[row_idx]["quantity"] >= quantity:
                # 해당 제품의 구매 수량을 quantity만큼 늘려줌
                self.purchasing_list[row_idx]["quantity"] -= quantity
            else:
                QMessageBox.information(
                    self, "ERROR!", f"{product_name}을 {quantity}만큼 뺄 수 없습니다."
                )

            # 만약 구매 목록에 방금 제외한 제품이 하나도 없다면 구매 목록에서 제외
            if self.purchasing_list[row_idx]["quantity"] == 0:
                del self.purchasing_list[row_idx]

        # 만약 구매 목록에 없는 상품인 경우 삭제 실패 메시지를 띄워줌
        else:
            QMessageBox.information(
                self, "ERROR!", f"{product_name}가 구매 목록에 없습니다."
            )

        # 화면 갱신
        self.update_screen()

    # 현금 계산 기능
    def cash_pay(self):
        # 만약 아무 것도 구매 목록에 없는 경우
        if not self.purchasing_list:
            QMessageBox.information(
                self, "ERROR!", "구매 목록이 비어 있습니다."
            )
        # 구매 목록에 뭔가 있는 경우
        else:
            result_message = ""
            result_message += f"받은 금액: {self.total_price_widget.item(3, 0).text()} 원\n"
            result_message += f"결제 금액: {self.total_price_widget.item(2, 0).text()} 원\n"
            charge = int(self.total_price_widget.item(3,0).text())-int(self.total_price_widget.item(2,0).text())
            result_message += f"거스름 돈: {charge} 원"

            # 판매 기록 갱신
            self.update_sales_record()

            self.purchasing_list.clear()
            self.clear_screen()

            QMessageBox.information(
                self, "결제 완료", result_message
            )

    # 카드 계산 기능
    def card_pay(self):
        # 만약 아무 것도 구매 목록에 없는 경우
        if not self.purchasing_list:
            QMessageBox.information(
                self, "ERROR!", "구매 목록이 비어 있습니다."
            )
        # 구매 목록에 뭔가 있는 경우
        else:
            result_message = ""
            result_message += f"정가 총액: {self.total_price_widget.item(0, 0).text()} 원\n"
            result_message += f"할인 금액: {self.total_price_widget.item(1, 0).text()} 원\n"
            result_message += f"결제 금액: {self.total_price_widget.item(2, 0).text()} 원"

            # 판매 기록 갱신
            self.update_sales_record()

            self.purchasing_list.clear()
            self.clear_screen()

            QMessageBox.information(
                self, "결제 완료", result_message
            )

    def read_sales(self):
        f = open(f"./sales/{self.sales_datetime_info}.txt", 'r')
        result_sales =""
        while True:
            line = f.readline()
            if not line: break
            result_sales+=line
        f.close()
        result_sales += f"정가 총액 : {self.total_discountprice+self.total_profit}원\n"
        result_sales += f"총 할인액 : {self.total_discountprice}원\n"
        result_sales += f"총 매출액 : {self.total_profit}원"

        QMessageBox.information(
            self, "매출 정보", result_sales
        )

    # 판매 기록 갱신
    def update_sales_record(self):
        # 결제 시각 기록
        now = datetime.now()
        # 이번 결제의 총 판매액
        profit = 0
        sum_discount = 0
        dicta = {}

        with open(f"./sales/{self.sales_datetime_info}.txt", 'a') as f:
            f.write(f"{now.year}년 {now.month}월 {now.day}일 {now.hour}시 {now.minute}분 {now.second}초\n")

            # 결제 제품명, 수량, 가격
            for i in range(len(self.purchasing_list)):
                name = self.purchasing_list[i]["name"]
                quantity = self.purchasing_list[i]["quantity"]
                single_price = self.purchasing_list[i]["object"].calc_price(1)
                price = self.purchasing_list[i]["object"].calc_price(quantity)
                origin_price = self.purchasing_list[i]["object"].price
                origin_discount = origin_price-single_price
                discount = origin_discount * quantity
                profit += price
                sum_discount += discount
                f.write(f"{name}, {single_price}원, {quantity}개, 총 {price}원\n")

                if name in dicta:
                    dicta[name]+=quantity
                else:
                    dicta[name]=quantity


            # POS기 시작부터 현재 시점까지의 총 매출
            self.total_profit += profit
            self.total_discountprice += sum_discount
            self.dict1 += Counter(dicta)
            f.write(f"합계: {profit}원\n")
            f.write('-' * GUIPosWindow.SEPARATOR_LENGTH + '\n')

    # 매출 기록 파일 생성
    def create_record_file(self):
        if not os.path.exists("sales"):
            print("sales directory doesn't exists.")
            os.makedirs("sales")
            print("sales directory is created.")

        with open(f"./sales/{self.sales_datetime_info}.txt", 'w') as f:
            print(f"{self.sales_datetime_info}.txt is created.")

    # 화면을 갱신함(구매 목록, 총 구매액 등)
    def update_screen(self):
        # 화면 비우기
        self.clear_screen()

        total_price = 0     # 정가 기준 총액
        total_discount = 0  # 총 할인액

        # 구매 목록 채우기
        for row_idx in range(len(self.purchasing_list)):
            product_info: Product = self.purchasing_list[row_idx]["object"]
            name = product_info.name
            quantity = self.purchasing_list[row_idx]["quantity"]

            # 제품 정가
            product_price = product_info.price
            # 할인된 제품 하나의 가격
            discounted_price = product_info.calc_price(1)
            # 제품 1개당 할인액
            discount_amount = product_price - discounted_price
            # 할인 총액에 추가
            total_discount += discount_amount * quantity
            # 정가 기준 총액에 추가
            total_price += product_info.calc_price(quantity)
            # 0열: 제품명
            self.purchasing_list_widget.setItem(row_idx, 0, QTableWidgetItem(name))
            # 1열: 단가
            self.purchasing_list_widget.setItem(row_idx, 1, QTableWidgetItem(str(product_price)))
            # 2열: 할인액
            self.purchasing_list_widget.setItem(row_idx, 2, QTableWidgetItem(str(discount_amount)))
            # 3열: 수량
            self.purchasing_list_widget.setItem(row_idx, 3, QTableWidgetItem(str(quantity)))
            # 4열: 합계
            self.purchasing_list_widget.setItem(row_idx, 4, QTableWidgetItem(str(product_info.calc_price(quantity))))

        # "주문 금액"
        self.total_price_widget.setItem(0, 0, QTableWidgetItem(str(total_price+total_discount)))
        # "할인 금액"
        self.total_price_widget.setItem(1, 0, QTableWidgetItem(str(total_discount)))
        # "청구 금액"
        self.total_price_widget.setItem(2, 0, QTableWidgetItem(str(total_price)))

    # 모든 내용 지우기
    def clear_screen(self):
        # 구매 목록 비우기
        self.purchasing_list_widget.clearContents()
        # 총 구매액 정보창 비우기
        self.total_price_widget.clearContents()
