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
        tableWidget1 = QTableWidget(10, 6)
        tableWidget1.setHorizontalHeaderLabels(["코드", "제품명", "단가", "할인", "수량", "합계"])
        tableWidget1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget1.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget1.verticalHeader().setVisible(False)
        tableWidget1.resizeColumnsToContents()
        tableWidget1.resizeRowsToContents()
        tableWidget1.setMinimumSize(550, 500)

        # lowerlayout - left
        tableWidget2 = QTableWidget(3, 1)
        tableWidget2.setVerticalHeaderLabels(["합계", "할인", "총계"])
        tableWidget2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget2.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget2.horizontalHeader().setVisible(False)
        tableWidget2.resizeColumnsToContents()
        tableWidget2.resizeRowsToContents()
        tableWidget2.setMinimumSize(500, 100)

        # upperlayout - right
        menuBox = QGroupBox("메뉴")
        upperRightLayOut = QGridLayout()

        r, c = 3, 5
        __tmp_product_pairs = tuple((name, obj) for name, obj in self.product_datas.items())
        for i in range(len(__tmp_product_pairs)):
            product_name, product_obj = __tmp_product_pairs[i]
            upperRightLayOut.addWidget(Button(product_name, self.buttonClicked), i//c, i%c)

        menuBox.setLayout(upperRightLayOut)

        # lowerlayout - right
        paymentButton = Button("계산", self.buttonClicked)
        cancelButton = Button("취소", self.buttonClicked)
        salesButton = Button("매출 정보", self.buttonClicked)

        lowerRightLayout = QHBoxLayout()
        lowerRightLayout.addWidget(paymentButton)
        lowerRightLayout.addWidget(cancelButton)
        lowerRightLayout.addWidget(salesButton)

        # layout
        upperLayOut = QHBoxLayout()
        upperLayOut.addWidget(tableWidget1)
        upperLayOut.addWidget(menuBox)

        lowerLayOut = QHBoxLayout()
        lowerLayOut.addWidget(tableWidget2)
        lowerLayOut.addLayout(lowerRightLayout)

        layout = QVBoxLayout()
        layout.addLayout(upperLayOut)
        layout.addLayout(lowerLayOut)

        self.setLayout(layout)
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
            sys.exit(-1);

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
