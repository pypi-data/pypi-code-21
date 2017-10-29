import sys

from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtWidgets import QApplication, QTableView


class MxSpaceTableModel(QAbstractTableModel):
    pass


class MxSpaceTableView(QTableView):
    pass


def test_widget():

    app = QApplication(sys.argv)
    table_view = MxSpaceTableView()

    model = MxSpaceTableModel()
    table_view.setModel(model)
    table_view.show()
    sys.exit(app.exec_())

    # table_view.doubleClicked[QtCore.QModelIndex].connect(
    #     table_view.ItemDoubleClicked)

if __name__ == '__main__':
    test_widget()