'''Brainfuck interpreter'''

def __static_vars():
    '''Decorate, add static attr'''
    def decorate(func):
        '''The decorate'''
        setattr(func, 'stdin_buffer', [])
        return func
    return decorate

@__static_vars()
def __getchar():
    '''Return one char from stdin'''
    buffer_len = len(__getchar.stdin_buffer)
    if buffer_len == 0:
        __getchar.stdin_buffer = list(input().encode('ascii'))
        __getchar.stdin_buffer.append(10) # We need this enter to compact getchar from libc.
    ret_c, __getchar.stdin_buffer = __getchar.stdin_buffer[0], __getchar.stdin_buffer[1:]
    return ret_c

def __pre_execute(raw_code: str):
    '''Replace the [] with paired code pointer'''
    iptr = 0
    bracket = list()
    code = list(raw_code)
    code_len = len(code)
    while iptr < code_len:
        code[iptr] = [code[iptr], '']
        if code[iptr][0] == '[':
            bracket.append(iptr)
        elif code[iptr][0] == ']':
            piptr = bracket.pop()
            code[piptr][1], code[iptr][1] = iptr, piptr
        iptr += 1
    bracket_len = len(bracket)
    if bracket_len != 0:
        code = []
    return code

def __execute(code: list, stack_size: int):
    '''Run bf code'''
    iptr = 0
    sptr = 0
    stack = list(0 for _ in range(stack_size))
    code_len = len(code)
    while iptr < code_len:
        instruction = code[iptr][0]
        if instruction == '>':
            sptr += 1
        elif instruction == '<':
            sptr -= 1
        elif instruction == '+':
            stack[sptr] += 1
            if stack[sptr] == 256:
                stack[sptr] = 0
        elif instruction == '-':
            stack[sptr] -= 1
            if stack[sptr] == -1:
                stack[sptr] = 255
        elif instruction == '.':
            print(chr(stack[sptr]), end='')
        elif instruction == ',':
            stack[sptr] = __getchar()
        elif instruction == '[' and stack[sptr] == 0:
            iptr = code[iptr][1]
        elif instruction == ']' and stack[sptr] != 0:
            iptr = code[iptr][1]
        iptr += 1
    print("RET(stack[0]) = %d" % stack[0])

def run(raw_code: str = '', stack_size: int = 128):
    '''Interpreter the raw_code.
    If the raw_code is empty, the program will get string from input.
    '''
    if raw_code == '':
        raw_code = input('% ')
    code = __pre_execute(raw_code)
    __execute(code, stack_size)
