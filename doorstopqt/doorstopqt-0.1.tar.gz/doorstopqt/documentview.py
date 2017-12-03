from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .icon import Icon
from .categoryselector import CategorySelector
from markdown import markdown


class DocumentTreeView(QWidget):
    def __init__(self, parent=None):
        super(DocumentTreeView, self).__init__(parent)

        self.tree = QTreeView()
        self.tree.header().hide()
        self.tree.setIndentation(20)
        self.model = QStandardItemModel()

        self.category = None
        self.db = None
        self.editview = None
        self.icons = Icon()

        catselgrid = QHBoxLayout()
        catselgrid.setSpacing(10)
        catselgrid.setContentsMargins(0, 0, 0, 0)

        self.catselector = CategorySelector()
        self.catselector.callback(self.buildtree)

        self.newcatbtn = QPushButton(self.icons.FileDialogNewFolder, '')
        self.newcatbtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        catselgrid.addWidget(self.catselector)
        catselgrid.addWidget(self.newcatbtn)

        self.selectionclb = None
        oldSelectionChanged = self.tree.selectionChanged
        def selectionChanged(selected, deselected):
            if self.selectionclb is not None:
                self.selectionclb(self.selecteduid())

            oldSelectionChanged(selected, deselected)
        self.tree.selectionChanged = selectionChanged
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.contextmenu)
        self.tree.setModel(self.model)

        self.grid = QVBoxLayout()
        catsel = QWidget()
        catsel.setLayout(catselgrid)
        self.grid.addWidget(catsel)
        self.grid.addWidget(self.tree)
        self.setLayout(self.grid)

        self.lastselected = {}
        self.collapsed = set()
        self.tree.collapsed.connect(lambda x: self.collapsed.add(self.uidfromindex(x)))
        self.tree.expanded.connect(lambda x: self.collapsed.discard(self.uidfromindex(x)))

        self.uid_to_item = {}

        copyshortcut = QShortcut(QKeySequence("Ctrl+C"), self.tree)
        def copy():
            if self.clipboard is None:
                return
            return self.clipboard(str(self.selecteduid()))
        copyshortcut.activated.connect(copy)

    def contextmenu(self, pos):
        menu = QMenu(parent=self.tree)
        si = self.tree.selectedIndexes()

        def createdocument(sibling=True):
            level = None
            lastsibling = None
            if len(si) > 0:
                if sibling:
                    parent = self.model.itemFromIndex(si[0]).parent()
                    if parent is not None:
                        data = self.model.data(self.model.indexFromItem(parent), Qt.UserRole)
                        level = str(data.level).split('.')
                        lastsibling = parent.child(parent.rowCount() - 1)
                else:
                    cur = self.model.itemFromIndex(si[0])
                    rows = cur.rowCount()
                    if rows == 0:
                        lastsibling = cur
                    else:
                        lastsibling = cur.child(rows - 1)
                    data = self.model.data(si[0], Qt.UserRole)
                    level = str(data.level)

            if lastsibling is None:
                rows = self.model.rowCount()
                lastsibling = self.model.itemFromIndex(self.model.index(rows - 1, 0))
                level = ['1']

            data = self.model.data(self.model.indexFromItem(lastsibling), Qt.UserRole)
            if data is not None:
                level = str(data.level).split('.')[:len(level)]
                level[-1] = str(int(level[-1]) + 1)
            if len(level) < 2:
                level.append('0')
            level = '.'.join(level)
            item = self.db.root.add_item(self.category, level=level)
            self.db.reload()

        if len(si) > 0:
            data = self.model.data(si[0], Qt.UserRole)
            act = menu.addAction(self.icons.FileIcon, 'Create sibling document')
            act.triggered.connect(lambda: createdocument())
            act = menu.addAction(self.icons.FileIcon, 'Create child document')
            act.triggered.connect(lambda: createdocument(False))
            if str(data.level).split('.')[-1] != '0':
                act.setEnabled(False)

            menu.addSeparator()
            act = menu.addAction('Remove document')
            def removedocument(uid):
                self.db.root.remove_item(uid)
                self.db.reload()
            act.triggered.connect(lambda: removedocument(data.uid))
        else:
            act = menu.addAction(self.icons.FileIcon, 'Create document')
            act.triggered.connect(lambda: createdocument())
        menu.addSeparator()
        menu.addAction('Expand all').triggered.connect(lambda: self.tree.expandAll())
        def collapse():
            self.tree.collapseAll()
            self.tree.clearSelection()
        menu.addAction('Collapse all').triggered.connect(collapse)
        menu.popup(self.tree.mapToGlobal(pos))

    def buildtree(self, cat=None):
        self.lastselected[str(self.category)] = self.selecteduid()
        self.model.clear()
        if self.db is None or len(self.db.root.documents) == 0:
            return
        if cat is None:
            if self.category is not None:
                cat = self.category
            else:
                cat = self.db.root.documents[0].prefix
        self.category = cat
        c = [x for x in self.db.root if x.prefix == cat][0]
        items = {}
        for doc in sorted(c, key=lambda x: x.level):
            level = str(doc.level)
            level = level.split('.')
            if level[-1] == '0':
                level = level[:-1]
            level = '.'.join(level)
            uid = str(doc.uid)
            item = QStandardItem()
            self.uid_to_item[str(doc.uid)] = [item, doc]
            item.setData(doc, Qt.UserRole)
            items[level] = item
            up = level.split('.')[:-1]
            up = '.'.join(up)
            if up != level and up in items:
                items[up].appendRow(item)
            else:
                self.model.appendRow(item)
            index = self.model.indexFromItem(item)
            if str(doc.uid) not in self.collapsed:
                self.tree.expand(index)
            if str(cat) in self.lastselected and str(doc.uid) == self.lastselected[str(cat)]:
                self.tree.setCurrentIndex(index)
            self.updateuid(uid)
        if len(self.tree.selectedIndexes()) == 0:
            self.tree.setCurrentIndex(self.model.index(0, 0))

    def connectdb(self, db):
        self.db = db
        self.buildtree()
        self.catselector.connectdb(db)

    def connectview(self, view):
        self.editview = view

    def connectcreatecatdiag(self, createcatdiag):
        self.createcatdiag = createcatdiag
        self.newcatbtn.clicked.connect(self.createcatdiag.show)

    def uidfromindex(self, index):
        data = self.model.data(index, role=Qt.UserRole)
        if data is not None:
            return str(data.uid)
        return None

    def selecteduid(self):
        selected = self.tree.selectedIndexes()
        if len(selected) > 0:
            return self.uidfromindex(selected[0])
        return None

    def updateuid(self, uid):
        if uid not in self.uid_to_item:
            return
        item = self.uid_to_item[uid][0]
        data = self.uid_to_item[uid][1]
        level = str(data.level)
        if data.heading:
            heading = data.text
            heading = markdown(heading.split('\n')[0])
            text = QTextDocument()
            text.setHtml(heading)
            title = '{} {}'.format(level, text.toPlainText())
        else:
            title = '{} {}'.format(level, uid)
        item.setText(title)

    def read(self, uid):
        if self.db is None:
            return
        item = self.db.find(uid)
        cat = str(item.parent_documents[0])
        self.lastselected[cat] = str(uid)
        self.catselector.select(cat)
