import sys, os
from PyQt5.QtWidgets import *
from datetime import datetime
from PyQt5.QtCore import pyqtSlot, Qt

from CUI_POS.tools import read_interface_file

from CUI_POS.core import Product
# from CUI_POS import function
import pdb


class Button(QToolButton):

    def __init__(self, text, callback):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setText(text)
        self.clicked.connect(callback)



class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        product_info_lines = read_interface_file(Product.PRODUCT_INTERFACE_FILENAME, "../")
        if len(product_info_lines) == 0:
            raise Product.InterfaceFileIsEmpty

        product_datas = {pair[0]: pair[1] for pair in map(Product.get_code_product_pair, product_info_lines)}

        #upperlayout- left
        tableWidget1 = QTableWidget(10, 6)
        tableWidget1.setHorizontalHeaderLabels(["코드", "제품명", "단가", "할인", "수량", "합계"])
        tableWidget1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget1.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget1.verticalHeader().setVisible(False)
        tableWidget1.resizeColumnsToContents()
        tableWidget1.resizeRowsToContents()
        tableWidget1.setMinimumSize(550,500)

        #lowerlayout - left
        tableWidget2 = QTableWidget(3, 1)
        tableWidget2.setVerticalHeaderLabels(["합계", "할인", "총계"])
        tableWidget2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget2.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget2.horizontalHeader().setVisible(False)
        tableWidget2.resizeColumnsToContents()
        tableWidget2.resizeRowsToContents()
        tableWidget2.setMinimumSize(500,100)

        #upperlayout - right
        menuBox = QGroupBox("메뉴")
        upperRightLayOut = QGridLayout()
        r = 2
        c = 0
        menuButton = product_datas
        for i in menuButton:
            menuButton[i] = Button(i, self.buttonClicked)
            upperRightLayOut.addWidget(menuButton[i], r, c)
            c += 1
            if c > 4:
                c = 0
                r -= 1

        menuBox.setLayout(upperRightLayOut)

        #lowerlayout - right
        paymentButton = Button("계산",self.buttonClicked)
        cancelButton = Button("취소",self.buttonClicked)
        salesButton = Button("매출 정보",self.buttonClicked)

        lowerRightLayout = QHBoxLayout()
        lowerRightLayout.addWidget(paymentButton)
        lowerRightLayout.addWidget(cancelButton)
        lowerRightLayout.addWidget(salesButton)

        #layout
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
        # print(key)
        """Row = 0
        if key in self.product_datas:
            row = Row
            self.tableWidget1.setItem(row,1,QTableWidgetItem(key))
            Row += 1
"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()