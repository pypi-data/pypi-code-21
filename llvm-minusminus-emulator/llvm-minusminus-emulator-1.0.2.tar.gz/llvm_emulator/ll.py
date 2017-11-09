"""Data structure for LLVM AST."""

from collections import namedtuple
from enum import Enum


class SimpleType(Enum):
    """Simple types in LLVM."""

    Void = 1
    I1 = 2
    I8 = 3
    I32 = 4
    I64 = 5

    def __repr__(self):
        if self == SimpleType.Void:
            return 'void'
        elif self == SimpleType.I1:
            return 'i1'
        elif self == SimpleType.I8:
            return 'i8'
        elif self == SimpleType.I32:
            return 'i32'
        elif self == SimpleType.I64:
            return 'i64'
        else:
            return str(self)


Program = namedtuple('Program', ['tdecls', 'gdecls', 'fdecls'])

TypeDec = namedtuple('TypeDec', ['name', 'body'])
PointerType = namedtuple('PointerType', ['inner_ty'])
StructType = namedtuple('StructType', ['fields'])
ArrayType = namedtuple('ArrayType', ['length', 'inner_ty'])
FunctionType = namedtuple('FunctionType', ['return_ty', 'parameters'])
NamedType = namedtuple('NamedType', ['other_name'])

GlobalDec = namedtuple('GlobalDec', ['name', 'ty', 'body'])
GNull = namedtuple('GNull', [])
GGid = namedtuple('GGid', ['val'])
GInt = namedtuple('GInt', ['val'])
GString = namedtuple('GString', ['val'])
GArray = namedtuple('GArray', ['entries'])
GStruct = namedtuple('GStruct', ['fields'])

FunctionDec = namedtuple('FunctionDec', ['return_type', 'name', 'parameters', 'body'])
FunctionBody = namedtuple('FunctionBody', ['first_block', 'named_blocks'])
Block = namedtuple('Block', ['insns', 'terminator'])

Binop = namedtuple('Binop', ['bop', 'ty',  'left', 'right'])
Alloca = namedtuple('Alloca', ['ty'])
Load = namedtuple('Load', ['ty', 'location'])
Store = namedtuple('Store', ['ty', 'value', 'location'])
Icmp = namedtuple('Icmp', ['cnd', 'ty', 'left', 'right'])
Call = namedtuple('Call', ['return_ty', 'callee', 'arguments'])
Bitcast = namedtuple('Bitcast', ['from_ty', 'oper', 'to_ty'])
Gep = namedtuple('Gep', ['base_ty', 'oper_ty', 'oper', 'steps'])
Zext = namedtuple('Zext', ['from_ty', 'oper', 'to_ty'])
Ptrtoint = namedtuple('Ptrtoint', ['pointer_ty', 'oper', 'to_ty'])

CallResult = namedtuple('CallResult', ['val'])

Ret = namedtuple('Ret', ['ty', 'oper'])
Br = namedtuple('Br', ['label'])
Cbr = namedtuple('Cbr', ['ty', 'oper', 'then_label', 'else_label'])

Null = namedtuple('Null', [])
Const = namedtuple('Const', ['val'])
Gid = namedtuple('Gid', ['val'])
Id = namedtuple('Id', ['val'])


def ty2s(ty):
    if isinstance(ty, SimpleType):
        return repr(ty)
    elif isinstance(ty, PointerType):
        return ty2s(ty.inner_ty) + '*'
    elif isinstance(ty, StructType):
        return ('{{{}}}'
                .format(', '.join(map(ty2s, ty.fields))))
    elif isinstance(ty, ArrayType):
        return ('[{} x {}]'
                .format(ty.length, ty2s(ty.inner_ty)))
    elif isinstance(ty, FunctionType):
        print('TODO: ty2s: FunctionType')
        return '<func>'
    elif isinstance(ty, NamedType):
        return '%' + ty.other_name
    else:
        print('ty2s: Unknown type: {}'
              .format(ty))
        return str(ty)


def oper2s(operand):
    if isinstance(operand, Null):
        return 'null'
    elif isinstance(operand, Const):
        return str(operand.val)
    elif isinstance(operand, Gid):
        return '@' + operand.val
    elif isinstance(operand, Id):
        return '%' + operand.val
    else:
        # TODO
        print('oper2s: Unknown operand: {}'
              .format(operand))


def tyopers2s(ty_oper_list):
    return ', '.join('{} {}'.format(ty2s(ty), oper2s(oper))
                     for ty, oper in ty_oper_list)


def insn2s(insn):
    if isinstance(insn, Binop):
        return ('{} {} {}, {}'
                .format(insn.bop, ty2s(insn.ty),
                        oper2s(insn.left), oper2s(insn.right)))
    if isinstance(insn, Alloca):
        return ('alloca {}'
                .format(ty2s(insn.ty)))
    if isinstance(insn, Load):
        return ('load {}, {}* {}'
                .format(ty2s(insn.ty), ty2s(insn.ty),
                        oper2s(insn.location)))
    if isinstance(insn, Store):
        return ('store {} {}, {}* {}'
                .format(ty2s(insn.ty),
                        oper2s(insn.value),
                        ty2s(insn.ty),
                        oper2s(insn.location)))
    elif isinstance(insn, Icmp):
        return ('icmp {} {} {}, {}'
                .format(insn.cnd, ty2s(insn.ty),
                        oper2s(insn.left), oper2s(insn.right)))
    elif isinstance(insn, Call):
        return ('call {} {} ({})'
                .format(ty2s(insn.return_ty), oper2s(insn.callee),
                        tyopers2s(insn.arguments)))
    elif isinstance(insn, Bitcast):
        return ('bitcast {} {} to {}'
                .format(ty2s(insn.from_ty), oper2s(insn.oper),
                        ty2s(insn.to_ty)))
    elif isinstance(insn, Gep):
        return ('getelementptr {}, {} {}, {}'
                .format(ty2s(insn.base_ty), ty2s(insn.oper_ty),
                        oper2s(insn.oper),
                        ', '.join('{} {}'.format(ty2s(t), oper2s(o))
                                  for t, o in insn.steps)))

    elif isinstance(insn, Zext):
        return ('zext {} {} to {}'
                .format(ty2s(insn.from_ty), oper2s(insn.oper),
                        ty2s(insn.to_ty)))
    elif isinstance(insn, Ptrtoint):
        return ('ptrtoint {}* {} to {}'
                .format(ty2s(insn.pointer_ty), oper2s(insn.oper),
                        ty2s(insn.to_ty)))
    elif isinstance(insn, CallResult):
        return ('<<internal>>: function return {}'
                .format(insn.val))
    else:
        # TODO
        print('insn2s: Unknown insn: {}'
              .format(insn))
        return '???'


def terminator2s(terminator):
    if isinstance(terminator, Ret):
        if terminator.oper is None:
            return ('ret {}'
                    .format(ty2s(terminator.ty)))
        else:
            return ('ret {} {}'
                    .format(ty2s(terminator.ty),
                            oper2s(terminator.oper)))
    elif isinstance(terminator, Br):
        return ('br label %{}'
                .format(terminator.label))
    elif isinstance(terminator, Cbr):
        return ('br {} {}, label %{}, label %{}'
                .format(ty2s(terminator.ty),
                        oper2s(terminator.oper),
                        terminator.then_label,
                        terminator.else_label))
    else:
        print('terminator2s: Unknown terminator {}'
              .format(terminator))


def ginit2s(ginit):
    if isinstance(ginit, GNull):
        return 'null'
    elif isinstance(ginit, GGid):
        return '@' + ginit.val
    elif isinstance(ginit, GInt):
        return str(ginit.val)
    elif isinstance(ginit, GString):
        return ('c"{}"'
                .format(ll_encode(ginit.val)))
    elif isinstance(ginit, GArray):
        return ('[{}]'
                .format(', '.join('{} {}'.format(ty2s(t), ginit2s(g))
                                  for t, g in ginit.entries)))
    elif isinstance(ginit, GStruct):
        return ('{{{}}}'
                .format(', '.join('{} {}'.format(ty2s(t), ginit2s(g))
                                  for t, g in ginit.fields)))


def gdecl2s(gdecl):
    return ('@{} = {} {}'
            .format(gdecl.name, ty2s(gdecl.ty), ginit2s(gdecl.body)))


def ll_encode(string):
    res_l = []
    for c in string:
        code = ord(c)
        if code <= 31 or code == 127:
            res_l.append('\{:02X}'.format(code))
        elif c == '\\':
            res_l.append('\\\\')
        elif c == '"':
            res_l.append('\\22')
        else:
            res_l.append(c)

    return ''.join(res_l)
