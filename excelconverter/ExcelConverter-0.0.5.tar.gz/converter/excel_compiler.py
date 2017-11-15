# Excel compiler.
# creates nodes from cells puts them in a graph and then puts that graph in a cellmap.
# Has several functions to set and calculate the changed values

import logging
import networkx as nx
from networkx.classes.digraph import DiGraph
from converter.excel_node import *
from converter.excel_util import *
from converter.excel_util import Cell
from converter.excel_lib import *  # Used dynamically in compiler
from converter.excel_wrapper import ExcelOpxWrapper as ExcelWrapperImpl
from converter.tokenizer import ExcelParser, f_token
import marshal

# Set the sheet into a node
def add_node_to_graph(g, n):
    g.add_node(n)
    g.node[n]['sheet'] = n.sheet

    if isinstance(n, Cell):
        g.node[n]['label'] = n.col + str(n.row)
    else:
        # strip the sheet
        g.node[n]['label'] = n.address()[n.address().find('!') + 1:]


class ExcelCompiler(object):
    def __init__(self, filename=None, *args, **kwargs):
        # Load file
        super(ExcelCompiler, self).__init__()
        self.filename = filename
        # Set the filename
        self.excel = ExcelWrapperImpl(filename=filename)
        self.excel.connect()

        self.log = logging.getLogger("decode.{0}".format(self.__class__.__name__))

    def cell2code(self, cell):
        # Generate python code for the given cell
        if cell.formula:
            e = shunting_yard(cell.formula or str(cell.value))
            ast, root = build_ast(e)
            code = root.emit(ast, context=Context(cell, self.excel))
        elif isinstance(cell.value, str) and re.match('[A-Za-z]+', cell.value):
            ast = None
            code = cell.value

        else:
            ast = None
            code = str('"' + cell.value + '"' if isinstance(cell.value, str) else cell.value)

        return code, ast

    def gen_graph(self, seed, sheet=None):
        # When given a starting point (e.g., A6 or A3:B7) on a particular sheet,
        # generate a Spreadsheet instance that captures the logic and control flow of the equations

        # starting points
        cursheet = sheet \
            if sheet else self.excel.get_active_sheet()
        self.excel.set_sheet(cursheet)

        seeds, nr, nc = Cell.make_cells(self.excel, seed,
                                        sheet=cursheet)  # no need to output NumberRows and NumberColoms here, since seed can be a list of unlinked cells
        seeds = list(flatten(seeds))

        print(("Seed %s expanded into %s cells" % (seed, len(seeds))))

        # only keep seeds with formulas or numbers
        # Scan seeds for data_types int of float
        seeds = [s for s in seeds if s.formula or isinstance(s.value, (int, float, str))]

        print(("%s filtered seeds " % len(seeds)))

        # cells to analyze: only formulas or strings
        # TODOMatthijs: check of het nog nodig is strings toe te voegen? moeten die nog verder worden verwerkt:
        # gecompileerd? Ze zitten immers ook in de seeds?
        todo = [s for s in seeds if s.formula or isinstance(s.value, str)]

        print(("%s cells on the todo list" % len(todo)))

        # map of all cells
        cellmap = dict([(x.address(), x) for x in seeds])

        # directed graph
        g = nx.DiGraph()

        # match the info in cellmap
        for c in list(cellmap.values()):
            add_node_to_graph(g, c)

        while todo:
            c1 = todo.pop()

            # set the current sheet so relative addresses resolve properly
            if c1.sheet != cursheet:
                cursheet = c1.sheet
                self.excel.set_sheet(cursheet)

            pystr, ast = self.cell2code(c1) # parse the formula into code
            c1.python_expression = pystr # set the code & compile it (will flag problems sooner rather than later)
            c1.compile()

            if ast is not None:
                # get all the cells/ranges this formula refers to
                deps = [x.tvalue.replace('$', '') for x in ast.nodes() if isinstance(x, RangeNode)]
                deps = uniqueify(deps) # remove dupes

                for dep in deps:
                        # if the dependency is a multi-cell range, create a range object
                    if is_range(dep):
                        # this will make sure we always have an absolute address
                        rng = CellRange(dep, value, sheet=cursheet)

                        if rng.address() in cellmap:
                            # already dealt with this range
                            # add an edge from the range to the parent
                            g.add_edge(cellmap[rng.address()], cellmap[c1.address()])
                            continue
                        else:
                            # turn into cell objects
                            cells, nrows, ncols = Cell.make_cells(self.excel, dep, sheet=cursheet)

                            # get the values so we can set the range value
                            if nrows == 1 or ncols == 1:
                                rng.value = [c.value for c in cells]
                            else:
                                rng.value = [[c.value for c in cells[i]] for i in range(len(cells))]

                            # save the range
                            cellmap[rng.address()] = rng
                            # add an edge from the range to the parent
                            add_node_to_graph(g, rng)
                            g.add_edge(rng, cellmap[c1.address()])
                            # cells in the range should point to the range as their parent
                            target = rng
                    else:
                        # not a range, create the cell object
                        cells = (Cell.resolve_cell(self.excel, dep, sheet=cursheet),)
                        target = cellmap[c1.address()]

                    # process each cell
                    for c2 in flatten(cells):
                        # Check that cells are None
                        if c2 is not None:
                            # if we havent treated this cell already
                            if c2.address() not in cellmap:
                                if c2.formula:
                                    # cell with a formula, needs to be added to the todo list
                                    todo.append(c2)
                                    # print("appended ", c2.address())

                                else:
                                    # constant cell, no need for further processing, just remember to set the code
                                    pystr, ast = self.cell2code(c2)
                                    c2.python_expression = pystr

                                    c2.compile()
                                # print("skipped ", c2.address())

                                # save in the cellmap
                                cellmap[c2.address()] = c2
                                # add to the graph
                                add_node_to_graph(g, c2)

                            # add an edge from the cell to the parent (range or cell)
                            g.add_edge(cellmap[c2.address()], target)

                # TODOMatthijs: kijk of onderstaande nog nodig is? (haal weg en run de tests)
                # Continue if it doesn't contain a formula (like a string cell), else the other formulas aren't compiled.
                if is_continue_Required(self, c2) or is_continue_Required(self, c1):
                    c2 = None
                    continue

        print(("Graph construction done, %s nodes, %s edges, %s cellmap entries" % (
        len(g.nodes()), len(g.edges()), len(cellmap))))
        sp = Spreadsheet(g, cellmap)
        return sp


def is_continue_Required(self, cell):
    cell is not None and cell.formula is None


def shunting_yard(expression):
    """
    Tokenize an excel formula expression into reverse polish notation

    Core algorithm taken from wikipedia with varargs extensions from
    http://www.kallisti.net.nz/blog/2008/02/extension-to-the-shunting-yard-algorithm-to-allow-variable-numbers-of-arguments-to-functions/
    """
    # remove leading =

    if expression.startswith('='):
        expression = expression[1:]

    p = ExcelParser()
    p.parse(expression)

    # insert tokens for '(' and ')', to make things clearer below
    tokens = []
    for t in p.tokens.items:
        if t.ttype == "function" and t.tsubtype == "start":
            t.tsubtype = ""
            tokens.append(t)
            tokens.append(f_token('(', 'arglist', 'start'))
        elif t.ttype == "function" and t.tsubtype == "stop":
            tokens.append(f_token(')', 'arglist', 'stop'))
        elif t.ttype == "subexpression" and t.tsubtype == "start":
            t.tvalue = '('
            tokens.append(t)
        elif t.ttype == "subexpression" and t.tsubtype == "stop":
            t.tvalue = ')'
            tokens.append(t)
        else:
            tokens.append(t)

    # print "tokens: ", "|".join([x.tvalue for x in tokens])

    # http://office.microsoft.com/en-us/excel-help/calculation-operators-and-precedence-HP010078886.aspx
    operators = {':': Operator(':', 8, 'left'), '': Operator(' ', 8, 'left'), ',': Operator(',', 8, 'left'),
                 'u-': Operator('u-', 7, 'left'), '%': Operator('%', 6, 'left'), '^': Operator('^', 5, 'left'),
                 '*': Operator('*', 4, 'left'), '/': Operator('/', 4, 'left'), '+': Operator('+', 3, 'left'),
                 '-': Operator('-', 3, 'left'), '&': Operator('&', 2, 'left'), '=': Operator('=', 1, 'left'),
                 '<': Operator('<', 1, 'left'), '>': Operator('>', 1, 'left'), '<=': Operator('<=', 1, 'left'),
                 '>=': Operator('>=', 1, 'left'), '<>': Operator('<>', 1, 'left')}

    output = collections.deque()
    stack = []
    were_values = []
    arg_count = []

    for t in tokens:
        if t.ttype == "operand":

            output.append(create_node(t))
            if were_values:
                were_values.pop()
                were_values.append(True)

        elif t.ttype == "function":

            stack.append(t)
            arg_count.append(0)
            if were_values:
                were_values.pop()
                were_values.append(True)
            were_values.append(False)

        elif t.ttype == "argument":

            while stack and (stack[-1].tsubtype != "start"):
                output.append(create_node(stack.pop()))

            if were_values.pop():
                arg_count[-1] += 1
            were_values.append(False)

            if not len(stack):
                raise Exception("Mismatched or misplaced parentheses")

        elif t.ttype.startswith('operator'):

            if t.ttype.endswith('-prefix') and t.tvalue == "-":
                o1 = operators['u-']
            else:
                o1 = operators[t.tvalue]

            while stack and stack[-1].ttype.startswith('operator'):

                if stack[-1].ttype.endswith('-prefix') and stack[-1].tvalue == "-":
                    o2 = operators['u-']
                else:
                    o2 = operators[stack[-1].tvalue]

                if ((o1.associativity == "left" and o1.precedence <= o2.precedence)
                    or
                        (o1.associativity == "right" and o1.precedence < o2.precedence)):

                    output.append(create_node(stack.pop()))
                else:
                    break

            stack.append(t)

        elif t.tsubtype == "start":
            stack.append(t)

        elif t.tsubtype == "stop":

            while stack and stack[-1].tsubtype != "start":
                output.append(create_node(stack.pop()))

            if not stack:
                raise Exception("Mismatched or misplaced parentheses")

            stack.pop()

            if stack and stack[-1].ttype == "function":
                f = create_node(stack.pop())
                a = arg_count.pop()
                w = were_values.pop()
                if w:
                    a += 1
                f.num_args = a
                # print f, "has ",a," args"
                output.append(f)

    while stack:
        if stack[-1].tsubtype == "start" or stack[-1].tsubtype == "stop":
            raise Exception("Mismatched or misplaced parentheses")

        output.append(create_node(stack.pop()))

    # print "Stack is: ", "|".join(stack)
    # print "Ouput is: ", "|".join([x.tvalue for x in output])

    # convert to list
    result = [x for x in output]
    return result


def build_ast(expression):
    """build an AST from an Excel formula expression in reverse polish notation"""

    # use a directed graph to store the tree
    g = DiGraph()

    stack = []

    for n in expression:
        # Since the graph does not maintain the order of adding nodes/edges
        # add an extra attribute 'pos' so we can always sort to the correct order
        if isinstance(n, OperatorNode):
            if n.ttype == "operator-infix":
                arg2 = stack.pop()
                arg1 = stack.pop()
                g.add_node(arg1, {'pos': 1})
                g.add_node(arg2, {'pos': 2})
                g.add_edge(arg1, n)
                g.add_edge(arg2, n)
            else:
                arg1 = stack.pop()
                g.add_node(arg1, {'pos': 1})
                g.add_edge(arg1, n)

        elif isinstance(n, FunctionNode):
            args = [stack.pop() for _ in range(n.num_args)]
            args.reverse()
            for i, a in enumerate(args):
                g.add_node(a, {'pos': i})
                g.add_edge(a, n)
                # for i in range(n.num_args):
                #    G.add_edge(stack.pop(),n)
        else:
            g.add_node(n, {'pos': 0})

        stack.append(n)

    return g, stack.pop()


class Context(object):
    """A small context object that nodes in the AST can use to emit code"""

    def __init__(self, curcell, excel):
        # the current cell for which we are generating code
        self.curcell = curcell
        # a handle to an excel instance
        self.excel = excel


def create_node(t):
    """Simple factory function"""
    if t.ttype == "operand":
        if t.tsubtype == "range":
            return RangeNode(t)
        else:
            return OperandNode(t)
    elif t.ttype == "function":
        return FunctionNode(t)
    elif t.ttype.startswith("operator"):
        return OperatorNode(t)
    else:
        return ASTNode(t)


class Operator:
    """Small wrapper class to manage operators during shunting yard"""

    def __init__(self, value, precedence, associativity):
        self.value = value
        self.precedence = precedence
        self.associativity = associativity


class Spreadsheet(object):
    def __init__(self, g, cellmap):
        super(Spreadsheet, self).__init__()
        self.G = g
        self.cellmap = cellmap
        self.params = None

    def set_value(self, cell, val, is_addr=True):

        if is_addr:
            cell = self.cellmap[cell]

            if cell.value != val and not None:
                self.reset(cell)
                cell.value = val
            return cell.value

    def reset(self, cell):
        if cell.value is None:
            return

        map(self.reset, self.G.successors_iter(cell))

    def print_value_tree(self, addr, indent):
        cell = self.cellmap[addr]
        print(("%s %s = %s" % (" " * indent, addr, cell.value)))
        for c in self.G.predecessors_iter(cell):
            self.print_value_tree(c.address(), indent + 1)

    def recalculate(self, addr):
        for c in list(self.cellmap.values()):
            if isinstance(c, CellRange):
                self.evaluate_range(c, is_addr=False)
            else:
                self.evaluate(c, is_addr=False)
            return self.evaluate(c)

    def evaluate_range(self, rng, is_addr=True):

        if is_addr:
            rng = self.cellmap[rng]

        # its important that [] gets treated as false here
        if rng.value:
            return rng.value
        elif isinstance(rng.value, str):
            return rng.value

        cells, nrows, ncols = rng.celladdrs, rng.nrows, rng.ncols

        if 1 == nrows or 1 == ncols:
            data = [self.evaluate(c) for c in cells]
        else:
            data = [[self.evaluate(c) for c in cells[i]] for i in range(len(cells))]

        rng.value = data

        return data

    def evaluate(self, cell, is_addr=True):
        if is_addr:
            cell = self.cellmap[cell]

            if cell.value and cell.formula is not None:
                cell.value = value
            elif cell.value != value:
                return cell.value
            elif cell.value == cell._compiled_expression:
                return cell.value

        def eval_cell(address):
            return self.evaluate(address)

        def eval_range(rng):
            return self.evaluate_range(rng)

        try:
            print(("Evalling: %s, %s" % (cell.address(), cell.python_expression)))
            vv = eval(cell.compiled_expression) if is_eval_allowed(self, cell) else cell.compiled_expression
            # return eval(cell.compiled_expression) if is_eval_allowed(self, cell) else cell.compiled_expression
            # if isinstance(cell.compiled_expression, str) and re.match('[A-Za-z]+', cell.compiled_expression):
            #     vv = cell.compiled_expression
            # else:
            #     vv = eval(cell.compiled_expression)

            # print "Cell %s evalled to %s" % (cell.address(),vv)
            if vv is None:
                print(("WARNING %s is None" % (cell.address())))
            cell.value = vv
        except Exception as e:
            if str(e).startswith("Problem evalling"):
                raise e
            else:
                raise Exception("Problem evalling: %s for %s, %s" % (e, cell.address(), cell.python_expression))
        return cell.value

