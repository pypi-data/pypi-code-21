class Question:
    def __init__(self, indent, type, name, extra_cells, row_number):
        self.indent = indent
        self.type = type
        self.name = name
        self.extra_cells = extra_cells
        self.row_number = row_number
        self.properties = {
        "identifier": "Untitled_Question",
        "title": name,
        "autoIdentifier": True,
        "type": type
        }
        
class sub(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties['children'] = []
        self.properties["type"] = "group"
        self.properties["minOccurs"] = 1
        self.properties["maxOccurs"] = 1

class grp(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties['children'] = []
        self.properties["type"] = "group"

class clc(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "calculated"
        self.properties["calculate_expr"] = "<invalid>"
        self.properties["type_derived"] = "<invalid>"

class txt(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "text"

class txtm(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "text"
        self.properties["multi_line"] = True

class dec(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "decimal"

class int(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "integer"

class img(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "image"

class s1(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "select"
        self.properties["options"] = 'blank'

class sm(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "select"
        self.properties["multiple"] = True
        self.properties["options"] = 'blank'

class bc(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "barcode"

class sig(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "signature"

class sk(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "sketch"

class tel(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "phone_number"

class yn(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "boolean"

class dt(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "date"

class tm(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "time"

class dtm(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "datetime"

class loc(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "location"

class em(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "email"

class pwd(Question):
    def __init__(self, indent, type, name, extra_cells, row_number):
        super().__init__(indent, type, name, extra_cells, row_number)
        self.properties["type"] = "password"


