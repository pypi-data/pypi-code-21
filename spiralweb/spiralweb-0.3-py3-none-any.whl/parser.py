import sys
import os
import io
import ply.lex as lex
import ply.yacc as yacc
from .model import SpiralWebChunk, SpiralWebRef, SpiralWeb

# Lexing definitions

class SpiralWebLexer:
    tokens = ('DOC_DIRECTIVE', 
              'OPEN_PROPERTY_LIST',
              'CLOSE_PROPERTY_LIST',
              'EQUALS',
              'COMMA',
              'CHUNK_REFERENCE',
              'CODE_DIRECTIVE',
              'CODE_END_DIRECTIVE',
              'NEWLINE',
              'AT_DIRECTIVE',
              'TEXT')

    t_TEXT = '[^@\[\]=,\n]+'
    t_COMMA = r','
    t_DOC_DIRECTIVE = r'@doc'
    t_CODE_DIRECTIVE = r'@code'
    t_CODE_END_DIRECTIVE = r'@='
    t_OPEN_PROPERTY_LIST = r'\['
    t_CLOSE_PROPERTY_LIST = r']'
    t_EQUALS = r'='

    def t_AT_DIRECTIVE(self, t):
        r'@@'
        t.value = '@'
        return t

    def t_CHUNK_REFERENCE(self, t):
        r'[ \t]*@<[^\]\n]+>[ \t]*'
        inputString = t.value.rstrip()
        refStart = inputString.find('@<')

        t.value = {'indent' : inputString[0:refStart],
                   'ref' : inputString[refStart+2:len(inputString)-1]}
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        print("Illegal character '%s' on line %s" % (t.value[0], t.lineno))
        t.lexer.skip(1)

    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, optimize=False, debug=False, **kwargs)

    def lex(self, input):
        token_list = []

        self.build()
        self.lexer.input(input)

        while True:
            token = self.lexer.token()

            if not token: break
            token_list
    

# Parser definitions

class SpiralWebParser:
    starting = 'web'
    tokens = []

    def __init__(self):
        self.tokens = SpiralWebLexer.tokens
        self.build()

    def p_error(self, p):
        print("Syntax error at token %(name)s at line %(line)i" % \
                {"line": p.lineno, "name": p.type })
        yacc.errok()

    def p_web(self, p):
        '''web : webtl web
               | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_webtl(self, p):
        '''webtl : codedefn
                 | docdefn
                 | doclines'''
        p[0] = p[1]

    def p_empty(self, p):
        'empty :'
        pass

    def p_doclines(self, p):
        '''doclines : TEXT
                    | NEWLINE
                    | AT_DIRECTIVE
                    | COMMA
                    | OPEN_PROPERTY_LIST
                    | CLOSE_PROPERTY_LIST
                    | EQUALS'''
        doc = SpiralWebChunk()
        doc.type = 'doc'
        doc.name = ''
        doc.options = {}
        doc.lines = [p[1]]
        p[0] = doc

    def p_docdefn(self, p):
        '''docdefn : DOC_DIRECTIVE TEXT optionalpropertylist NEWLINE doclines'''
        doc = SpiralWebChunk()
        doc.type = 'doc'
        doc.name = p[2].strip()
        doc.options = p[3]
        doc.lines = [p[5]]
        p[0] = doc

    def p_codedefn(self, p):
        '''codedefn : CODE_DIRECTIVE TEXT optionalpropertylist NEWLINE codelines CODE_END_DIRECTIVE
                    '''
        code = SpiralWebChunk()
        code.type = 'code'
        code.name = p[2].strip()
        code.options = p[3]
        code.lines = p[5]
        p[0] = code

    def p_codelines(self, p):
        '''codelines : codeline codelines
                     | empty'''
        if len(p) == 3:
           p[0] = [p[1]] + p[2]
        else:
           p[0] = []

    def p_codeline(self, p):
        '''codeline : TEXT 
                    | NEWLINE
                    | AT_DIRECTIVE
                    | OPEN_PROPERTY_LIST
                    | CLOSE_PROPERTY_LIST
                    | COMMA
                    | EQUALS
                    | chunkref'''
        doc = SpiralWebChunk()
        doc.type = 'doc'
        doc.name = ''
        doc.options = {}
        doc.lines = [p[1]]
        p[0] = doc

    def p_chunkref(self, p):
        '''chunkref : CHUNK_REFERENCE'''
        p[0] = SpiralWebRef(p[1]['ref'], p[1]['indent'])

    def p_optionalpropertylist(self, p):
        '''optionalpropertylist : propertylist 
                                | empty'''

        if p[1] == None:
           p[0] = {}
        else:
            p[0] = p[1]

    def p_propertylist(self, p):
        '''propertylist : OPEN_PROPERTY_LIST propertysequence CLOSE_PROPERTY_LIST'''
        p[0] = p[2]

    def p_propertysequence(self, p):
        '''propertysequence : empty 
                            | propertysequence1'''
        p[0] = p[1]

    def p_propertysequence1(self, p):
        '''propertysequence1 : property 
                             | propertysequence1 COMMA property'''
        if len(p) == 2:
           p[0] = p[1]
        else:
           p[0] = dict(list(p[1].items()) + list(p[3].items()))

    def p_property(self, p):
        '''property : TEXT EQUALS TEXT'''
        p[0] = {p[1] : p[3]}

    def build(self,**kwargs):
        self.lexer = SpiralWebLexer()
        self.lexer.build()

        self.parser = yacc.yacc(module=self, optimize=False, debug=False, **kwargs)

    def parse(self, input):
        return self.parser.parse(input)
    

def parse_webs(input_strings):
    output = {}

    stderr_ = sys.stderr
    sys.stderr = io.StringIO("")

    parser = SpiralWebParser()

    for key, input in input_strings.items():
        output[key] = parser.parse(input)

    sys.stderr = stderr_

    return output


