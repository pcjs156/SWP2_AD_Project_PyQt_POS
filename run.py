import sys

from PyQt5.QtWidgets import QApplication

from CUI_POS.core import POSCore
from GUI_POS.gui_pos import GUIPosWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pos = GUIPosWindow()
    pos.show()
    app.exec_()

    # pos_cui = POSCore()
    # pos_cui.run()