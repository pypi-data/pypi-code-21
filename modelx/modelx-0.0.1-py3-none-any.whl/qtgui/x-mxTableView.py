from PyQt5 import QtWidgets
from PyQt5 import QtCore
import sys


class MyTableView(QtWidgets.QTableView):
    def ItemDoubleClicked(self, index):
        QtWidgets.QMessageBox.information(None, "Hello!",
                                          "You Double Clicked: \n" + index.data())


def main():
    app = QtWidgets.QApplication(sys.argv)
    tableView = MyTableView(None)
    model = QtCore.QStringListModel()

    model.setStringList(["Item 1", "Item 2", "Item 3", "Item 4"])
    tableView.setModel(model)
    tableView.setWindowTitle("QTableView Detect Double Click")
    tableView.show()

    tableView.doubleClicked[QtCore.QModelIndex].connect(
        tableView.ItemDoubleClicked)
    return app.exec_()


if __name__ == '__main__':
    main()