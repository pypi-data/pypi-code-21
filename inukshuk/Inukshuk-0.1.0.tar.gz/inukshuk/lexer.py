import io


TOKEN_ID_NONE = 0
TOKEN_ID_TEXT = 1
TOKEN_ID_WHITESPACE = 2
TOKEN_ID_COMMENT = 3

TOKEN_ID_STRING_SINGLE_QUOTES = 5
TOKEN_ID_STRING_DOUBLE_QUOTES = 6
TOKEN_ID_INTEGER = 7
TOKEN_ID_FLOAT = 8

TOKEN_ID_EXPRESSION_BEGIN = 10
TOKEN_ID_EXPRESSION_END = 11

TOKEN_ID_STATEMENT_BEGIN = 20
_TID_ST_BEGIN_TRIM_WS = 21
_TID_ST_BEGIN_ADD_WS = 22
TOKEN_ID_STATEMENT_END = 25
_TID_ST_END_TRIM_WS = 26
_TID_ST_END_ADD_WS = 27

TOKEN_ID_IDENTIFIER = 30
TOKEN_ID_SYMBOL = 31


def _get_public_token_id(tid):
    if tid == _TID_ST_BEGIN_TRIM_WS or tid == _TID_ST_BEGIN_ADD_WS:
        return TOKEN_ID_STATEMENT_BEGIN
    if tid == _TID_ST_END_TRIM_WS or tid == _TID_ST_END_ADD_WS:
        return TOKEN_ID_STATEMENT_END
    return tid


# match functions should return True/False.
# consume functions should return (token ID, next pos)
#      ...with optional tuple items (is in inukshuk syntax, start offset,
#                                    end offset, force yield)


EXPRESSION_BEGIN, EXPRESSION_END = ('{{', '}}')
STATEMENT_BEGIN, STATEMENT_END = ('{%', '%}')
COMMENT_BEGIN, COMMENT_END = ('{#', '#}')

SYMBOLS = '.:,!=+-*/<>|()[]~'

PASSTHROUGH_STOP_CHAR = EXPRESSION_BEGIN[0]


def rule_expression_start(text, index, text_len, is_in_inukshuk):
    if not is_in_inukshuk and text[index:index + 2] == EXPRESSION_BEGIN:
        return (TOKEN_ID_EXPRESSION_BEGIN, index + 2, True)
    return None


def rule_expression_end(text, index, text_len, is_in_inukshuk):
    if is_in_inukshuk and text[index:index + 2] == EXPRESSION_END:
        return (TOKEN_ID_EXPRESSION_END, index + 2, False)
    return None


def rule_statement_start(text, index, text_len, is_in_inukshuk):
    if not is_in_inukshuk and text[index:index + 2] == STATEMENT_BEGIN:
        end_idx = index + 2

        tid = TOKEN_ID_STATEMENT_BEGIN
        if text_len > end_idx:
            c = text[end_idx]
            if c == '-':
                tid = _TID_ST_BEGIN_TRIM_WS
                end_idx += 1
            elif c == '+':
                tid = _TID_ST_BEGIN_ADD_WS
                end_idx += 1

        return (tid, end_idx, True)

    return None


def rule_statement_end(text, index, text_len, is_in_inukshuk):
    if is_in_inukshuk:
        is_match = False
        end_idx = index + 2
        tid = TOKEN_ID_STATEMENT_END

        if text[index] == '-':
            tid = _TID_ST_END_TRIM_WS
            is_match = text[index + 1:index + 3] == STATEMENT_END
            end_idx += 1
        elif text[index] == '+':
            tid = _TID_ST_END_ADD_WS
            is_match = text[index + 1:index + 3] == STATEMENT_END
            end_idx += 1
        else:
            is_match = text[index:index + 2] == STATEMENT_END

        if is_match:
            return (tid, end_idx, False)

    return None


def rule_comment(text, index, text_len, is_in_inukshuk):
    if not is_in_inukshuk and text[index:index + 2] == COMMENT_BEGIN:
        next_index = text.find(COMMENT_END, index + 2, text_len)
        if next_index < 0:
            # TODO: parse error?
            next_index = text_len
        return (TOKEN_ID_COMMENT, next_index + 2, False, 2, 2)

    return None


def rule_identifier(text, index, text_len, is_in_inukshuk):
    if is_in_inukshuk:
        o = ord(text[index])

        # [a-zA-Z_]
        if ((97 <= o <= 122) or (65 <= o <= 90) or o == 95):
            index += 1

            # [a-zA-Z0-9_]
            while index < text_len:
                o = ord(text[index])
                if (not (
                        (97 <= o <= 122) or
                        (65 <= o <= 90) or
                        (48 <= o <= 57) or
                        (o == 95))):
                    break
                index += 1
            return (TOKEN_ID_IDENTIFIER, index)

    return None


def rule_number(text, index, text_len, is_in_inukshuk):
    if is_in_inukshuk:
        o = ord(text[index])

        # [0-9]
        if (48 <= o <= 57):
            index += 1

            # [0-9]
            while index < text_len:
                o = ord(text[index])
                if not (48 <= o <= 57):
                    break
                index += 1

            tid = TOKEN_ID_INTEGER

            # Is it a float? (look for a `.`)
            if index < text_len - 1 and text[index] == '.':
                after_dot = ord(text[index + 1])
                if 48 <= after_dot <= 57:
                    # It's a float! Consume the decimals.
                    index += 1
                    tid = TOKEN_ID_FLOAT
                    while index < text_len:
                        o = ord(text[index])
                        if not (48 <= o <= 57):
                            break
                        index += 1

            return (tid, index)

    return None


def rule_symbols(text, index, text_len, is_in_inukshuk):
    if is_in_inukshuk and text[index] in SYMBOLS:
        # Force yield each symbol individually.
        return (TOKEN_ID_SYMBOL, index + 1, is_in_inukshuk, 0, 0, True)
    return None


def rule_whitespace(text, index, text_len, is_in_inukshuk):
    if is_in_inukshuk:
        next_index = index
        while next_index < text_len:
            c = text[next_index]
            if c == ' ' or c == '\t' or c == '\r' or c == '\n':
                next_index += 1
            else:
                break

        if next_index > index:
            return (TOKEN_ID_WHITESPACE, next_index)

    return None


def rule_string(text, index, text_len, is_in_inukshuk):
    c = text[index]
    tid = TOKEN_ID_NONE
    if is_in_inukshuk and (c == '"' or c == "'"):
        index += 1
        next_index = index
        tid = (TOKEN_ID_STRING_DOUBLE_QUOTES if c == '"'
               else TOKEN_ID_STRING_SINGLE_QUOTES)
        while index < text_len:
            # Find the same type of quote as the opening one.
            closing = text.find(c, index, text_len)
            if closing >= 0:
                if text[closing - 1] == '\\':
                    # The character was escaped... keep looking.
                    index += 1
                    continue
                next_index = closing + 1
            else:
                next_index = text_len
            break

        return (tid, next_index, is_in_inukshuk, 1, 1)

    return None


def rule_passthrough(text, index, text_len, is_in_inukshuk):
    if not is_in_inukshuk:
        # Don't check the stop character on the first index because if
        # we ended up in this lexer rule, it means none of the other rules
        # matched so we need to at least consume one character.
        # This happens typically if there's a single `{` in the text.
        next_index = text.find(PASSTHROUGH_STOP_CHAR, index + 1, text_len)
        if next_index < 0:
            next_index = text_len

        return (TOKEN_ID_TEXT, next_index)

    return None


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, engine=None, rules=None):
        self.lstrip_blocks = False
        self.rstrip_blocks = False
        self.rules = []
        if rules:
            self.rules += rules
        self.rules.append(rule_whitespace)
        self.rules.append(rule_identifier)
        self.rules.append(rule_string)
        self.rules.append(rule_number)
        self.rules.append(rule_expression_start)
        self.rules.append(rule_statement_start)
        self.rules.append(rule_expression_end)
        self.rules.append(rule_statement_end)
        self.rules.append(rule_comment)
        # Symbols rule needs to happen after all the rules that match
        # characters that look like symbols.
        self.rules.append(rule_symbols)
        # Always last
        self.rules.append(rule_passthrough)

    def tokenize(self, text):
        pos = 0
        end_pos = len(text)
        line_num = 1
        is_in_inukshuk = False
        current_token_id = TOKEN_ID_NONE
        current_token_stream = io.StringIO()
        last_token_id = TOKEN_ID_NONE

        # Loop optimization...
        rules = self.rules
        lstrip_blocks = self.lstrip_blocks
        rstrip_blocks = self.rstrip_blocks
        stream_write = current_token_stream.write
        stream_get = current_token_stream.getvalue
        stream_seek = current_token_stream.seek
        stream_truncate = current_token_stream.truncate

        # Start tokenizing!
        while pos < end_pos:
            active_rule = None
            rule_result = None
            for r in rules:
                rule_result = r(text, pos, end_pos, is_in_inukshuk)
                if rule_result is not None:
                    active_rule = r
                    break
            if rule_result is None:
                raise LexerError(
                    "Error line %d: Can't match any rule, "
                    "even the pass-through one! Currently at: %s" %
                    (line_num, text[pos:pos + 10]))

            tid = rule_result[0]
            next_pos = rule_result[1]
            if next_pos == pos:
                raise LexerError(
                    "Error line %d: Rule '%s' didn't consume any text, "
                    "at: %s" %
                    (line_num, active_rule, text[pos:pos + 10]))

            result_len = len(rule_result)
            if result_len > 2:
                is_in_inukshuk = rule_result[2]

            start_offset = 0
            end_offset = 0
            if result_len > 4:
                start_offset = rule_result[3]
                end_offset = rule_result[4]

            force_yield = False
            if result_len > 5:
                force_yield = rule_result[5]

            if tid != current_token_id or force_yield:
                value = stream_get()
                if current_token_id == TOKEN_ID_TEXT:
                    value = _process_text_token(
                        lstrip_blocks, rstrip_blocks,
                        last_token_id, current_token_id, value, tid)

                # If the token type has changed, return the finished token
                if current_token_id != TOKEN_ID_NONE:
                    pub_tid = _get_public_token_id(current_token_id)
                    yield (line_num, pub_tid, value)

                last_token_id = current_token_id

                current_token_id = tid
                stream_seek(0)
                stream_truncate()

            # Continue building the current token.
            stream_write(text[pos + start_offset:next_pos - end_offset])

            # Keep track of the current line.
            line_num += text.count('\n', pos, next_pos)

            # Advance!
            pos = next_pos

        # Return the last token we had before the string ended.
        if current_token_id != TOKEN_ID_NONE:
            value = current_token_stream.getvalue()
            if current_token_id == TOKEN_ID_TEXT:
                value = _process_text_token(
                    lstrip_blocks, rstrip_blocks,
                    last_token_id, current_token_id, value, TOKEN_ID_NONE)
            pub_tid = _get_public_token_id(current_token_id)
            yield (line_num, pub_tid, value)


def _process_text_token(lstrip_blocks, rstrip_blocks,
                        last_token_id, token_id, value, next_token_id):
    # Strip the left of the text if the previous block needs
    # to be stripped on the right.
    if (last_token_id == _TID_ST_END_TRIM_WS or
            (rstrip_blocks and
             last_token_id != _TID_ST_END_ADD_WS)):
        value = _lstrip_spaces_and_first_newline(value)
    # Same on the other side.
    if (next_token_id == _TID_ST_BEGIN_TRIM_WS or
            (lstrip_blocks and
             next_token_id != _TID_ST_BEGIN_ADD_WS)):
        value = _rstrip_spaces_until_newline(value)

    return value


def _lstrip_spaces_and_first_newline(text):
    text_len = len(text)
    if text_len == 0:
        return text

    index = 0
    while index < text_len and (text[index] == ' ' or text[index] == '\t'):
        index += 1
    if index < text_len and text[index] == '\r':
        index += 1
    if index < text_len and text[index] == '\n':
        index += 1

    if index < text_len:
        return text[index:]
    return ''


def _rstrip_spaces_until_newline(text):
    index = len(text) - 1
    while index >= 0 and (text[index] == ' ' or text[index] == '\t'):
        index -= 1
    if index < 0:
        return ''
    if text[index] == '\r' or text[index] == '\n':
        return text[:index + 1]
    return text
