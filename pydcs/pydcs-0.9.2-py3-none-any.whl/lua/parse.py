def loads(tablestr):

    class Parser:

        def __init__(self, buffer: str):
            self.buffer = buffer
            self.buflen = len(buffer)
            self.pos = 0  # type: int
            self.lineno = 1  # type: int

        def value(self):
            self.eat_ws()

            c = self.buffer[self.pos]
            if c == '{':
                return self.object()
            elif c == '"':
                return self.string()
            elif c.isnumeric() or c == '-':
                return self.number()
            elif c == '_':
                return self.str_function()
            else:  # varname
                varname = self.eatvarname()
                if varname == 'false' or varname == 'true':
                    return varname == 'true'
                if varname == 'local':
                    # ignore local keyword
                    self.eat_ws()
                    varname = self.eatvarname()
                self.eat_ws()
                if not self.eob() and self.buffer[self.pos] == '=':
                    self.pos += 1
                    return {varname: self.value()}
                else:
                    se = SyntaxError()
                    se.text = varname + " '" + self.buffer[self.pos] + "'"
                    se.lineno = self.lineno
                    se.offset = self.pos
                    raise se

            return {}

        def str_function(self):
            if self.buffer[self.pos] != '_':
                se = SyntaxError()
                se.lineno = self.lineno
                se.offset = self.pos
                se.text = "Expected character '_', got '{char}'".format(char=self.buffer[self.pos])
                raise se

            if self.advance():
                raise self.eob_exception()

            self.eat_ws()

            if self.buffer[self.pos] != '(':
                se = SyntaxError()
                se.lineno = self.lineno
                se.offset = self.pos
                se.text = "Expected character '(', got '{char}'".format(char=self.buffer[self.pos])
                raise se

            self.advance()
            self.eat_ws()

            s = self.string()

            self.eat_ws()

            if self.buffer[self.pos] != ')':
                se = SyntaxError()
                se.lineno = self.lineno
                se.offset = self.pos
                se.text = "Expected character ')', got '{char}'".format(char=self.buffer[self.pos])
                raise se

            self.pos += 1
            return s


        def string(self):
            if self.buffer[self.pos] != '"':
                se = SyntaxError()
                se.lineno = self.lineno
                se.offset = self.pos
                se.text = "Expected character '\"', got '{char}'".format(char=self.buffer[self.pos])
                raise se

            state = 0
            s = ''
            while state != 1:
                if self.advance():
                    raise self.eob_exception()

                c = self.buffer[self.pos]
                if state == 0:
                    if c == '"':
                        state = 1
                        self.pos += 1
                    elif c == '\\':
                        state = 2
                    else:
                        s += c
                elif state == 2:
                    s += c
                    state = 0
            return s

        def number(self):
            n = ''
            sign = 1
            if self.buffer[self.pos] == '-':
                sign = -1
                if self.advance():
                    raise self.eob_exception()

            while (not self.eob() and
                    (self.buffer[self.pos].isnumeric() or self.buffer[self.pos] == '.' or
                        self.buffer[self.pos].lower() == 'e')):
                n += self.buffer[self.pos]
                self.pos += 1

            num = float(n) * sign
            if num.is_integer():
                return int(num)
            return num

        def object(self):
            d = {}
            if self.buffer[self.pos] != '{':
                se = SyntaxError()
                se.lineno = self.lineno
                se.offset = self.pos
                se.text = "Expected character '{', got '{char}'".format(char=self.buffer[self.pos])
                raise se

            if self.advance():
                raise self.eob_exception()

            self.eat_ws()

            while self.buffer[self.pos] != '}':
                self.eat_ws()

                if self.buffer[self.pos] != '[':
                    se = SyntaxError()
                    se.lineno = self.lineno
                    se.offset = self.pos
                    se.text = "Expected character '[', got '{char}'".format(char=self.buffer[self.pos])
                    raise se

                if self.advance():
                    raise self.eob_exception()

                self.eat_ws()
                if self.buffer[self.pos] == '"':
                    key = self.string()
                else:
                    key = self.number()

                if self.eob():
                    raise self.eob_exception()

                self.eat_ws()

                if self.buffer[self.pos] != ']':
                    se = SyntaxError()
                    se.lineno = self.lineno
                    se.offset = self.pos
                    se.text = "Expected character ']', got '{char}'".format(char=self.buffer[self.pos])
                    raise se

                if self.advance():
                    raise self.eob_exception()

                self.eat_ws()

                if self.buffer[self.pos] != '=':
                    se = SyntaxError()
                    se.lineno = self.lineno
                    se.offset = self.pos
                    se.text = "Expected character '=', got '{char}'".format(char=self.buffer[self.pos])
                    raise se

                if self.advance():
                    raise self.eob_exception()

                val = self.value()

                self.eat_ws()

                d[key] = val
                # print(key, ':', val)

                c = self.buffer[self.pos]
                if c == '}':
                    break
                elif c == ',':
                    if self.advance():
                        raise self.eob_exception()
                    self.eat_ws()
                else:
                    se = SyntaxError()
                    se.lineno = self.lineno
                    se.offset = self.pos
                    se.text = "Unexpected character '{char}'".format(char=self.buffer[self.pos])
                    raise se

            self.pos += 1

            return d

        def eatvarname(self):
            varname = ''
            while (not self.eob()) and self.buffer[self.pos].isalnum():
                varname += self.buffer[self.pos]
                self.pos += 1

            return varname

        def eat_comment(self):
            if (self.buffer[self.pos] == '-' and
                self.pos + 1 < self.buflen and
                self.buffer[self.pos + 1] == '-'):
                while not self.eob() and self.buffer[self.pos] != '\n':
                    self.pos += 1

        def eat_ws(self):
            self.eat_comment()
            while True:
                if self.pos >= self.buflen:
                    return
                c = self.buffer[self.pos]  # type: str
                if c == '\n':
                    self.lineno += 1
                if c == '-':
                    self.eat_comment()
                    c = self.buffer[self.pos]
                if not c.isspace():
                    return

                self.pos += 1

        def eob(self):
            return self.pos >= self.buflen

        def eob_exception(self):
            se = SyntaxError()
            se.lineno = self.lineno
            se.offset = self.pos
            se.text = "Unexpected end of buffer"
            return se

        def char(self):
            return self.buffer[self.pos]

        def advance(self):
            self.pos += 1
            return self.eob()

    p = Parser(tablestr)
    return p.value()
