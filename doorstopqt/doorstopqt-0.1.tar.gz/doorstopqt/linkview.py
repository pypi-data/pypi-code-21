from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from markdown import markdown
import doorstop.core.item
from .icon import Icon


class LinkItemModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(LinkItemModel, self).__init__(parent)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            item = self.itemFromIndex(index)
            data = item.data()
            if type(data) is str:
                return data
            elif type(data) is tuple:
                is_parent_link = data[0]
                is_suspect = data[2]
                data = data[1]
                text = QTextDocument()
                text.setHtml(markdown(data.text.split('\n')[0]))
                suspect = '[needs review] ' if is_suspect else ''
                text = suspect + str(data) + '\t' + text.toPlainText()
                if is_parent_link:
                    return '→ ' + text
                else:
                    return '← ' + text
            return ''

        return super(LinkItemModel, self).data(index, role)


class LinkView(QListView):
    def __init__(self, parent=None):
        super(LinkView, self).__init__(parent)

        self.icons = Icon()
        self.db = None
        self.model = LinkItemModel()
        self.setModel(self.model)
        self.setAlternatingRowColors(True)
        self.linkentry = None
        def dataChanged(index):
            if self.db is None:
                return
            if self.currentuid is None:
                return
            item = self.model.itemFromIndex(index)
            data = item.data()
            uid = item.text()
            doc = self.db.find(uid)
            if doc is not None:
                self.db.root.link_items(self.currentuid, uid)

            self.read(self.currentuid)
        self.model.dataChanged.connect(dataChanged)

        def clicked(index):
            item = self.model.itemFromIndex(index)
            if item.isEditable():
                self.edit(index)
        self.clicked.connect(clicked)

        def dblclicked(index):
            item = self.model.itemFromIndex(index)
            data = item.data()
            if data is None or item.isEditable():
                return
            data = data[1]
            self.goto(data.uid)
        self.doubleClicked.connect(dblclicked)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextmenu)

        delete = QShortcut(QKeySequence("Delete"), self)
        delete.activated.connect(self.remove_selected_link)

    def contextmenu(self, pos):
        if self.db is None:
            return
        if self.currentuid is None:
            return
        menu = QMenu(parent=self)
        si = self.selectedIndexes()

        if len(si) == 0:
            return

        item = self.model.itemFromIndex(si[0])
        data = item.data()
        if type(data) is not tuple:
            return

        is_suspect = data[2]
        data = data[1]

        act = menu.addAction(self.icons.ArrowForward, 'Go to {}'.format(str(data.uid)))
        act.triggered.connect(lambda: self.goto(data.uid))
        if data.uid in self.db.find(self.currentuid).links:
            act = menu.addAction('Mark link as reviewed')
            act.setEnabled(is_suspect)
            act.triggered.connect(lambda: self.review_link(data.uid))
        else:
            act = menu.addAction("Can't mark child links as reviewed")
            act.setEnabled(False)
        act = menu.addAction(self.icons.DialogCloseButton, 'Remove link')
        act.triggered.connect(self.remove_selected_link)
        menu.popup(self.mapToGlobal(pos))

    def connectdb(self, db):
        self.db = db

    def read(self, uid):
        if self.db is None:
            return

        self.currentuid = None

        data = self.db.find(uid)
        self.model.clear()
        self.linkentry = QStandardItem()
        self.linkentry.setData('<Click here to add parent link>')
        self.model.appendRow(self.linkentry)
        for link in data.links:
            d = self.db.find(str(link))
            item = QStandardItem(str(link))
            suspect = link.stamp != self.db.find(link).stamp()
            item.setData((True, d, suspect))
            item.setEditable(False)
            self.model.appendRow(item)

        clinks = data.find_child_links()
        for clink in clinks:
            d = self.db.find(str(clink))
            item = QStandardItem(str(clink))
            item.setData((False, d, False))
            item.setEditable(False)
            self.model.appendRow(item)

        while self.model.rowCount() < 5:
            item = QStandardItem()
            item.setEditable(False)
            item.setSelectable(False)
            self.model.appendRow(item)

        self.currentuid = uid

    def remove_selected_link(self):
        if self.db is None:
            return
        if self.currentuid is None:
            return
        si = self.selectedIndexes()

        if len(si) == 0:
            return

        item = self.model.itemFromIndex(si[0])
        data = item.data()
        if type(data) is not tuple:
            return
        data = data[1]
        if data.uid not in self.db.find(self.currentuid).links:
            return

        self.db.root.unlink_items(self.currentuid, data.uid)
        self.read(self.currentuid)

    def review_link(self, uid):
        if self.db is None:
            return
        if self.currentuid is None:
            return
        cur = self.db.find(self.currentuid)
        for link in cur.links:
            if link == uid:
                link.stamp = self.db.find(uid).stamp()
        cur.save()
        self.read(self.currentuid)

    def goto(self, uid):
        if self.gotoclb:
            self.gotoclb(uid)
