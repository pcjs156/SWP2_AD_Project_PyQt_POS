import sys
from PyQt5.QtWidgets import *

from CUI_POS.tools import read_interface_file

from CUI_POS.core import Product


class Button(QToolButton):
    def __init__(self, text, callback):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setText(text)
        self.clicked.connect(callback)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 파일 불러오기
        product_info_lines = read_interface_file(Product.PRODUCT_INTERFACE_FILENAME, "../")
        if len(product_info_lines) == 0:
            raise Product.InterfaceFileIsEmpty
        self.product_datas = {pair[0]: pair[1] for pair in map(Product.get_code_product_pair, product_info_lines)}

        self.initUI()

    def initUI(self):
        # upperlayout- left
        self.purchasing_list_widget = QTableWidget(10, 6)
        self.purchasing_list_widget.setHorizontalHeaderLabels(["코드", "제품명", "단가", "할인", "수량", "합계"])
        self.purchasing_list_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.purchasing_list_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.purchasing_list_widget.verticalHeader().setVisible(False)
        self.purchasing_list_widget.resizeColumnsToContents()
        self.purchasing_list_widget.resizeRowsToContents()
        self.purchasing_list_widget.setMinimumSize(550, 500)

        # lowerlayout - left
        self.total_price_widget = QTableWidget(3, 1)
        self.total_price_widget.setVerticalHeaderLabels(["합계", "할인", "총계"])
        self.total_price_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.total_price_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.total_price_widget.horizontalHeader().setVisible(False)
        self.total_price_widget.resizeColumnsToContents()
        self.total_price_widget.resizeRowsToContents()
        self.total_price_widget.setMinimumSize(500, 100)

        # upperlayout - right
        self.menuBox = QGroupBox("메뉴")
        self.upperRightLayOut = QGridLayout()

        r, c = 3, 5
        __tmp_product_pairs = tuple((name, obj) for name, obj in self.product_datas.items())
        for i in range(len(__tmp_product_pairs)):
            product_name, product_obj = __tmp_product_pairs[i]
            self.upperRightLayOut.addWidget(Button(product_name, self.buttonClicked), i//c, i%c)

        self.menuBox.setLayout(self.upperRightLayOut)

        # lowerlayout - right
        self.payment_button = Button("계산", self.buttonClicked)
        self.cancel_button = Button("취소", self.buttonClicked)
        self.sales_button = Button("매출 정보", self.buttonClicked)

        self.function_layout = QHBoxLayout()
        self.function_layout.addWidget(self.payment_button)
        self.function_layout.addWidget(self.cancel_button)
        self.function_layout.addWidget(self.sales_button)

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

        # 제품 버튼을 누른 경우
        if key in self.product_datas.keys():
            product = self.product_datas[key]
            print(f"제품 '{key}'가 눌렸습니다: 정가 {product.price}원 / 할인 {product.discount_rate}% / 할인가 {product.calc_price(1)}")

        # 계산 버튼을 누른 경우
        elif key == "계산":
            print("계산 키가 눌렸습니다.")
            pass

        # 취소 버튼을 누른 경우
        elif key == "취소":
            print("취소 키가 눌렸습니다.")
            pass

        # 매출 정보 버튼을 누른 경우
        elif key == "매출 정보":
            print("매출 정보 키가 눌렸습니다.")
            pass

        else:
            print("알 수 없는 버튼입니다.")
            sys.exit(-1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
