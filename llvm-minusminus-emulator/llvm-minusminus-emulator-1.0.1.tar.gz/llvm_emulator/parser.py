"""Parser for LLVM--."""

import ply.lex as lex
import ply.yacc as yacc

from llvm_emulator import ll


class LLVMParser(object):
    # Lexer

    current_string = ""
    line_begin = 0

    states = [
        ('string', 'exclusive')
    ]

    reserved = {
        'add': 'ADD',
        'sub': 'SUB',
        'mul': 'MUL',
        'shl': 'SHL',
        'lshr': 'LSHR',
        'ashr': 'ASHR',
        'and': 'AND',
        'or': 'OR',
        'xor': 'XOR',
        'sdiv': 'SDIV',
        'eq': 'EQ',
        'ne': 'NE',
        'slt': 'SLT',
        'sle': 'SLE',
        'sgt': 'SGT',
        'sge': 'SGE',
        'alloca': 'ALLOCA',
        'load': 'LOAD',
        'store': 'STORE',
        'icmp': 'ICMP',
        'call': 'CALL',
        'bitcast': 'BITCAST',
        'getelementptr': 'GETELEMENTPTR',
        'zext': 'ZEXT',
        'ptrtoint': 'PTRTOINT',
        'ret': 'RET',
        'br': 'BR',
        'label': 'LABEL',
        'define': 'DEFINE',
        'null': 'NULL',
        'global': 'GLOBAL',
        'type': 'TYPE',
        'to': 'TO',
        'void': 'VOID',
        'i1': 'I1',
        'i8': 'I8',
        'i32': 'I32',
        'i64': 'I64',
       }

    tokens = [
        'INT', 'STRING',
        'ASTERIX', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'LBRACE', 'RBRACE',
        'ASSIGN', 'COLON', 'COMMA',
        'PercentID', 'AtID', 'ID'
    ]

    t_ignore = ' \t'
    t_string_ignore = ''
    t_ASTERIX = r'\*'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACK = r'\['
    t_RBRACK = r'\]'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_ASSIGN = r'='
    t_COLON = r':'
    t_COMMA = r','

    def t_COMMENT(self, t):
        r'(;|declare|target).*'
        pass

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self.line_begin = t.lexpos

    def t_string_newline(self, t):
        r'\n'
        print("{}:{}: Newline is not allowed inside strings."
              .format(t.lineno, t.lexpos - self.line_begin))
        t.lexer.lineno += 1
        self.line_begin = t.lexpos

    def t_INT(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_begin_string(self, t):
        r'c\"'
        t.lexer.begin('string')
        self.current_string = ""

    def t_string_doublequote(self, t):
        r'\\"'
        self.current_string += '"'

    def t_string_backslash(self, t):
        r'\\\\'
        self.current_string += '\\'

    def t_string_hex(self, t):
        r'\\[0-9a-fA-F][0-9a-fA-F]'
        code = int(t.value[1:], 16)
        self.current_string += chr(code)

    def t_string_singlebackslash(self, t):
        r'\\'
        print("{}:{}: Single backslash is not allowed inside strings."
              .format(t.lineno, t.lexpos - self.line_begin))

    def t_string_end(self, t):
        r'"'
        t.value = self.current_string
        self.current_string = ""
        t.type = "STRING"
        t.lexer.begin('INITIAL')
        return t

    def t_string_meat(self, t):
        r'.'
        self.current_string += t.value

    def t_ID(self, t):
        r'[a-zA-Z0-9_-]+'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_PercentID(self, t):
        r'%[a-zA-Z0-9_-]+'
        t.value = t.value[1:]
        return t

    def t_AtID(self, t):
        r'@[a-zA-Z0-9_-]+'
        t.value = t.value[1:]
        return t

    def t_ANY_error(self, t):
        print("{}:{}: Illegal character '{}'"
              .format(t.lineno, t.lexpos - self.line_begin, t.value[0]))
        t.lexer.skip(1)

    # Parser
    def handle_top_decs(self, smth):
        tdecs = {}
        gdecs = {}
        fdecs = {}
        for top_dec in smth:
            name = top_dec.name
            if isinstance(top_dec, ll.FunctionDec):
                if name in fdecs.keys():
                    print('ERROR: Function {} is declared more than once'
                          .format(name))
                fdecs[name] = top_dec
            elif isinstance(top_dec, ll.TypeDec):
                if name in tdecs.keys():
                    print('ERROR: Type {} is declared more than once'
                          .format(name))
                tdecs[name] = top_dec
            elif isinstance(top_dec, ll.GlobalDec):
                if name in gdecs.keys():
                    print('ERROR: Global {} is declared more than once'
                          .format(name))
                gdecs[name] = top_dec
            else:
                print('Parser Error: Unknown top level declaration {}'
                      .format(top_dec))
        return tdecs, gdecs, fdecs

    def p_program(self, p):
        'program : top_decs'
        tdecls, gdecls, fdecls = self.handle_top_decs(p[1])
        p[0] = ll.Program(tdecls, gdecls, fdecls)

    def p_topdecs_some(self, p):
        '''top_decs : tdec top_decs
            | gdec top_decs
            | fdec top_decs'''
        p[0] = [p[1]] + p[2]

    def p_topdecs_empty(self, p):
        'top_decs : '
        p[0] = []

    def p_tdec(self, p):
        'tdec : PercentID ASSIGN TYPE ty'
        p[0] = ll.TypeDec(p[1], p[4])

    def p_ty_void(self, p):
        'ty : VOID'
        p[0] = ll.SimpleType.Void

    def p_ty_i1(self, p):
        'ty : I1'
        p[0] = ll.SimpleType.I1

    def p_ty_i8(self, p):
        'ty : I8'
        p[0] = ll.SimpleType.I8

    def p_ty_i32(self, p):
        'ty : I32'
        p[0] = ll.SimpleType.I32

    def p_ty_i64(self, p):
        'ty : I64'
        p[0] = ll.SimpleType.I64

    def p_ty_ptr(self, p):
        'ty : ty ASTERIX'
        p[0] = ll.PointerType(p[1])

    def p_ty_struct(self, p):
        'ty : LBRACE ty_list RBRACE'
        p[0] = ll.StructType(p[2])

    def p_ty_array(self, p):
        'ty : LBRACK INT ID ty RBRACK'
        if p[3] == 'x':
            p[0] = ll.ArrayType(p[2], p[4])
        else:
            print('Invalid name in array definition: {}\n  It should have been an x.'
                  .format(p[3]))
            raise SyntaxError

    def p_ty_fun(self, p):
        'ty : ty LPAREN ty_list RPAREN'
        p[0] = ll.FunctionType(p[1], p[3])

    def p_ty_id(self, p):
        'ty : PercentID'
        p[0] = ll.NamedType(p[1])

    def p_ty_list_single(self, p):
        'ty_list : ty'
        p[0] = [p[1]]

    def p_ty_list_multiple(self, p):
        'ty_list : ty COMMA ty_list'
        p[0] = [p[1]] + p[3]

    def p_ty_list_empty(self, p):
        'ty_list : '
        p[0] = []

    def p_gdec(self, p):
        'gdec : AtID ASSIGN GLOBAL ty ginit'
        p[0] = ll.GlobalDec(p[1], p[4], p[5])

    def p_ginit_null(self, p):
        'ginit : NULL'
        p[0] = ll.GNull()

    def p_ginit_id(self, p):
        'ginit : AtID'
        p[0] = ll.GGid(p[1])

    def p_ginit_int(self, p):
        'ginit : INT'
        p[0] = ll.GInt(p[1])

    def p_ginit_string(self, p):
        'ginit : STRING'
        p[0] = ll.GString(p[1])

    def p_ginit_array(self, p):
        'ginit : LBRACK ty_ginit_list RBRACK'
        # TODO This syntax seems weird
        p[0] = ll.GArray(p[2])

    def p_ginit_struct(self, p):
        'ginit : LBRACE ty_ginit_list RBRACE'
        p[0] = ll.GStruct(p[2])

    def p_ty_ginit_list_single(self, p):
        'ty_ginit_list : ty ginit'
        p[0] = [(p[1], p[2])]

    def p_ty_ginit_list_multiple(self, p):
        'ty_ginit_list : ty ginit COMMA ty_ginit_list'
        p[0] = [(p[1], p[2])] + p[4]

    def p_ty_ginit_list_empty(self, p):
        'ty_ginit_list : '
        p[0] = []

    def p_fdec(self, p):
        'fdec : DEFINE ty AtID LPAREN ty_id_list RPAREN LBRACE fbody RBRACE'
        p[0] = ll.FunctionDec(p[2], p[3], p[5], p[8])

    def p_ty_id_list_single(self, p):
        'ty_id_list : ty PercentID'
        p[0] = [(p[1], p[2])]

    def p_ty_id_list_multiple(self, p):
        'ty_id_list : ty PercentID COMMA ty_id_list'
        p[0] = [(p[1], p[2])] + p[4]

    def p_ty_id_list_empty(self, p):
        'ty_id_list : '
        p[0] = []

    def p_fbody_multiple_blocks(self, p):
        'fbody : block named_block_list'
        named_blocks = {label: block for (label, block) in p[2]}
        p[0] = ll.FunctionBody(p[1], named_blocks)

    def p_fbody_one_block(self, p):
        'fbody : block'
        p[0] = ll.FunctionBody(p[1], [])

    def p_block_insns_terminator(self, p):
        'block : insns terminator'
        p[0] = ll.Block(p[1], p[2])

    def p_block_terminator(self, p):
        'block : terminator'
        p[0] = ll.Block([], p[1])

    def p_insns_single(self, p):
        'insns : optionally_named_insn'
        p[0] = [p[1]]

    def p_insns_multiple(self, p):
        'insns : optionally_named_insn insns'
        p[0] = [p[1]] + p[2]

    def p_optionally_named_insn_some(self, p):
        'optionally_named_insn : PercentID ASSIGN insn'
        p[0] = (p[1], p[3])

    def p_optionally_named_insn_none(self, p):
        'optionally_named_insn : insn'
        p[0] = (None, p[1])

    def p_insn_bop(self, p):
        'insn : bop ty operand COMMA operand'
        p[0] = ll.Binop(p[1], p[2], p[3], p[5])

    def p_insn_alloca(self, p):
        'insn : ALLOCA ty'
        p[0] = ll.Alloca(p[2])

    def p_insn_load(self, p):
        'insn : LOAD ty COMMA ty operand'
        p[0] = ll.Load(p[2], p[5])

    def p_insn_store(self, p):
        'insn : STORE ty operand COMMA ty operand'
        p[0] = ll.Store(p[2], p[3], p[6])

    def p_insn_icmp(self, p):
        'insn : ICMP cnd ty operand COMMA operand'
        p[0] = ll.Icmp(p[2], p[3], p[4], p[6])

    def p_insn_call(self, p):
        'insn : CALL ty operand LPAREN ty_operand_list RPAREN'
        p[0] = ll.Call(p[2], p[3], p[5])

    def p_insn_call_empty(self, p):
        'insn : CALL ty operand LPAREN RPAREN'
        p[0] = ll.Call(p[2], p[3], [])

    def p_insn_bitcast(self, p):
        'insn : BITCAST ty operand TO ty'
        p[0] = ll.Bitcast(p[2], p[3], p[5])

    def p_insn_gep(self, p):
        'insn : GETELEMENTPTR ty COMMA ty operand COMMA ty_operand_list'
        p[0] = ll.Gep(p[2], p[4], p[5], p[7])

    def p_insn_gep_empty(self, p):
        'insn : GETELEMENTPTR ty COMMA ty operand'
        p[0] = ll.Gep(p[2], p[4], p[5], [])

    def p_insn_zext(self, p):
        'insn : ZEXT ty operand TO ty'
        p[0] = ll.Zext(p[2], p[3], p[4])

    def p_insn_ptrtoint(self, p):
        'insn : PTRTOINT ty ASTERIX operand TO ty'
        p[0] = ll.Ptrtoint(p[2], p[4], p[6])

    def p_bop(self, p):
        '''bop : ADD
            | SUB
            | MUL
            | SHL
            | LSHR
            | ASHR
            | AND
            | OR
            | XOR
            | SDIV'''
        p[0] = p[1]

    def p_cnd(self, p):
        '''cnd : EQ
            | NE
            | SLT
            | SLE
            | SGT
            | SGE'''
        p[0] = p[1]

    def p_ty_operand_list_single(self, p):
        'ty_operand_list : ty operand'
        p[0] = [(p[1], p[2])]

    def p_ty_operand_list_multiple(self, p):
        'ty_operand_list : ty operand COMMA ty_operand_list'
        p[0] = [(p[1], p[2])] + p[4]

    def p_terminator_ret_void(self, p):
        'terminator : RET VOID'
        p[0] = ll.Ret(ll.SimpleType.Void, None)

    def p_terminator_ret_oper(self, p):
        'terminator : RET ty operand'
        p[0] = ll.Ret(p[2], p[3])

    def p_terminator_branch(self, p):
        'terminator : BR LABEL PercentID'
        p[0] = ll.Br(p[3])

    def p_terminator_conditional_branch(self, p):
        'terminator : BR ty operand COMMA LABEL PercentID COMMA LABEL PercentID'
        p[0] = ll.Cbr(p[2], p[3], p[6], p[9])

    def p_operand_null(self, p):
        'operand : NULL'
        p[0] = ll.Null()

    def p_operand_const(self, p):
        'operand : INT'
        p[0] = ll.Const(p[1])

    def p_operand_gid(self, p):
        'operand : AtID'
        p[0] = ll.Gid(p[1])

    def p_operand_id(self, p):
        'operand : PercentID'
        p[0] = ll.Id(p[1])

    def p_named_block_list_single(self, p):
        'named_block_list : ID COLON block'
        p[0] = [(p[1], p[3])]

    def p_named_block_list_multiple(self, p):
        'named_block_list : ID COLON block named_block_list'
        p[0] = [(p[1], p[3])] + p[4]

    def p_error(self, t):
        if t is None:
            print('Syntax error at end of file')
        else:
            print('Syntax error at token {}'
                  .format(t))

    def __init__(self):
        self.tokens += self.reserved.values()

    def build(self):
        """
        Build the parser.

        This method builds the parsing tables and initializes the
        internal lexer and parser variables. This method must be
        called prior to parsing.

        """
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    def parse(self, text):
        """
        Generate AST from text.

        Return a AST representation of the llvm program from text.

        """
        return self.parser.parse(text, lexer=self.lexer)
