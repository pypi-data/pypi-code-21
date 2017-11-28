from ..nodes.base import MultiChildrenParserNode


class Extension:
    def setupEngine(self, engine):
        pass

    def getGlobals(self):
        return {}

    def getFilters(self):
        return {}

    def getTests(self):
        return {}

    def getStatementNodes(self):
        return []


class StatementNode(MultiChildrenParserNode):
    name = None
    compiler_imports = None
