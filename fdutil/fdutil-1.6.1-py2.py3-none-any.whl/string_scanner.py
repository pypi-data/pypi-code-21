# encoding: utf-8

import logging

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


class StringScannerError(Exception):
    pass


class StringScanner(object):
    
    """
    Class to provide methods of searching,
    navigating and extracting portions of
    a string.
    Example use: parsing XML.
    """
    def __init__(self,
                 string):
        self.__string = string.rstrip()
        self.__index = 0
        self.__remembered_position = None
        self.__len = len(self.__string)

    def fwd(self):
        """
        Move to the next character
        """
        self.__index += 1

    def rev(self):
        """
        Move to the previous character
        """
        self.__index -= 1

    def read(self):
        """
        returns the current character and
        moves to the next character
        """
        # -----------------------------------------------------------------
        # Peek...
        try:
            peek = self.__string[self.__index]
        except IndexError:
            peek = None
        # -----------------------------------------------------------------
        self.__index += 1
        return peek

    def get_previous(self):
        """
        moves to the previous character and
        returns that character
        """
        self.__index -= 1
        # -----------------------------------------------------------------
        # Peek...
        try:
            return self.__string[self.__index]
        except IndexError:
            return None
        # -----------------------------------------------------------------

    def peek(self,
             length = 1):
        """
        Returns the next 'length' characters as a string
        index is unaltered
        """
        try:
            return self.__string[self.__index:self.__index + length]
        except IndexError:
            try:
                return self.__string[self.__index:]
            except IndexError:
                return None

    def __peek_1(self):
        """
        Returns the next 'length' characters as a string
        index is unaltered
        """
        try:
            return self.__string[self.__index]
        except IndexError:
            return None

    @property
    def _debug_peek(self):
        """
        returns the remainder without advancing the index
        Useful in debug as the property is evaluated.
        """
        return self.__string[self.__index:self.__len]

    @property
    def eos(self):
        """
        Test for being at or past the end of the scanner
        """
        return self.__index >= self.__len

    @property
    def sos(self):
        """
        Test for being at or before the start of the scanner
        """
        return self.__index <= 0

    def reset(self):
        self.__index = 0

    def next_matches(self,
                     value):
        """
        True if the next set of characters match the string.
        """
        try:
            return value == self.__string[self.__index:self.__index + len(value)]
        except IndexError:
            try:
                return value == self.__string[self.__index:]
            except IndexError:
                return False

    def find(self,
             value):
        """
        Move pointer to the next instance of
        the character (if there is one).
        If already at the matching character, will not move
        """
        self.__index = self.__string.find(value, self.__index)

    def remember_position(self):
        """
        Stores the current position for restoration later.
        NOTE: Only stores one position.
        """
        self.__remembered_position = self.__index

    def restore_position(self):
        """
        Restores the position to the previously
        stored position.
        """
        if self.__remembered_position is None:
            raise StringScannerError(u'Attempting to restore before remembering the position. Can only restore once!')
        self.__index = self.__remembered_position
        self.__remembered_position = None

    def skip_over(self,
                  end_value):
        """
        skips through through the string looking for
        the end value. Positions index at the next
        position after that.
        """
        end_value_len = len(end_value)
        # -----------------------------------------------------------------
        # Peek...
        try:
            peek = self.__string[self.__index:self.__index + end_value_len]
        except IndexError:
            try:
                peek = self.__string[self.__index:]
            except IndexError:
                peek = None
        # -----------------------------------------------------------------

        while not peek == end_value and not self.__index >= self.__len:
            self.__index += 1
            # -----------------------------------------------------------------
            # Peek...
            try:
                peek = self.__string[self.__index:self.__index + end_value_len]
            except IndexError:
                try:
                    peek = self.__string[self.__index:]
                except IndexError:
                    peek = None
            # -----------------------------------------------------------------

        if not self.__index >= self.__len:
            self.__index += end_value_len

    def skip_any(self,
                 value_to_skip):
        """
        skips past a value_to_skip or multiple
        consecutive instances of a value_to_skip
        does not skip if the value is not next
        """
        len_value_to_skip = len(value_to_skip)
        # -----------------------------------------------------------------
        # Peek...
        try:
            peek = self.__string[self.__index:self.__index + len_value_to_skip]
        except IndexError:
            try:
                peek = self.__string[self.__index:]
            except IndexError:
                peek = None
        # -----------------------------------------------------------------

        while peek == value_to_skip and not self.__index >= self.__len:
            self.__index += len_value_to_skip
            # -----------------------------------------------------------------
            # Peek...
            try:
                peek = self.__string[self.__index:self.__index + len_value_to_skip]
            except IndexError:
                try:
                    peek = self.__string[self.__index:]
                except IndexError:
                    peek = None

            # -----------------------------------------------------------------

    def skip_whitespace(self):
        """
        skips past a value_to_skip or multiple
        consecutive instances of a value_to_skip
        does not skip if the value is not next
        """
        while not self.__index >= self.__len and self.__peek_1() <= u' ':
            self.__index += 1

    def check_and_skip(self,
                       sequence):
        """
        checks that the next sequence matches
        the given sequence and skips if it does.
        """

        sequence_len = len(sequence)
        try:
            peek = self.__string[self.__index:self.__index + sequence_len]
        except IndexError:
            try:
                peek = self.__string[self.__index:]
            except IndexError:
                peek = None

        if peek == sequence:

            # -----------------------------------------------------------------
            # Peek...
            try:
                peek = self.__string[self.__index:self.__index + sequence_len]
            except IndexError:
                try:
                    peek = self.__string[self.__index:]
                except IndexError:
                    peek = None
            # -----------------------------------------------------------------
            while not peek == sequence and not self.__index >= self.__len:
                self.__index += 1
                # -----------------------------------------------------------------
                # Peek...
                try:
                    peek = self.__string[self.__index:self.__index + sequence_len]
                except IndexError:
                    try:
                        peek = self.__string[self.__index:]
                    except IndexError:
                        peek = None
                # -----------------------------------------------------------------

            if not self.__index >= self.__len:
                self.__index += sequence_len

        else:
            raise StringScannerError(u'Value "{value}" not found at index:{index}'
                                     .format(value=sequence,
                                             index=self.__index))

    def read_until_value_reached(self,
                                 value):
        """
        returns a string from the current position
        to the first instance of value or to
        the end of the scanner.
        EXCLUDES value
        """
        start = self.__index
        i = self.__string.find(value, start)
        self.__index = self.__len if i < 0 else i
        return self.__string[start:self.__index]

    def read_until_value_read(self,
                              value):
        """
        returns a string from the current position
        to the first instance of a string or to
        the end of the scanner.
        INCLUDES string
        """
        start = self.__index
        i = self.__string.find(value, start)
        self.__index = (self.__len
                        if i < 0
                        else (self.__len
                              if i + len(value) > self.__len
                              else i + len(value)))
        return self.__string[start:i]

    def read_between(self,
                     start,
                     end):
        """
        Returns the string in between start and
        end markers. Excludes markers.
        Scanner is positioned after the end marker
        EXCLUDES start and end
        """
        self.check_and_skip(start)
        read = self.read_until_value_reached(end)
        self.check_and_skip(end)
        return read

    def remainder(self):
        """
        returns the unread portion of the scanner
        """
        remainder = self.__string[self.__index:]
        self.__index = self.__len
        return remainder

    def line_line_number_and_column(self):
        if self.__index == 0:
            line_number = 1
            column      = 0
        else:
            lines = self.__string[:self.__index].splitlines()
            line_number = len(lines)
            column = len(lines[-1])
        line = self.__string.splitlines()[line_number - 1]
        return line, line_number, column

    def __error_message(self,
                        message):
        line, line_number, column = self.line_line_number_and_column()
        return u'{message} at line:{line_number}, column:{column}\n{line}\n{indicator}' \
               .format(message     = message,
                       line_number = line_number,
                       column      = column,
                       line        = line,
                       indicator   = u' ' * column + u'▲')

    def throw(self,
              message,
              exception=StringScannerError):
        error_message = self.__error_message(message)
        logging.error(error_message)
        raise exception(error_message)

    def log_error(self,
                  message):
        logging.error(self.__error_message(message))

    def log_warning(self,
                    message):
        logging.warning(self.__error_message(message))


def main():
    # TODO: Turn these into unit tests.
    s = StringScanner(u'   <  some text blah "some more text" >    \n'
                      u'<!-- This is a comment <a>with an embedded element!</> -->***    xx')
    s.find(u"<")
    assert s.peek() == u"<"
    assert s.read() == u"<"
    s.skip_any(u" ")
    assert s.peek() == u"s"
    a = s.read_until_value_read(u' ')
    assert a == u'some '
    print u'after "some ":"%s"' % s.peek
    print s.peek(7)
    assert s.peek(7) == u"text bl", u"'{value}'".format(value = s.peek(7))
    s.fwd()
    a = s.read()
    assert a == u'e', a
    a = s.read_until_value_read(u'some')
    assert a == u'xt blah "some', a
    assert s.peek() == u' ', s.peek()
    a = s.read_until_value_reached(u'text')
    assert a == u' more ', a
    s.find(u'<')
    if s.next_matches(u'<!--'):
        s.skip_over(u'-->')
    assert s.peek() == u"*", u'"'+s.peek()+u'"'
    s.skip_any(u' ')
    assert s.peek() == u"*", u'"'+s.peek()+u'"'
    s.skip_any(u' ')
    assert s.peek() == u"*", u'"'+s.peek()+u'"'
    s.read_until_value_read(u' ')
    s.skip_whitespace()
    assert s.peek() == u"x", u'"'+s.peek()+u'"'
    print u"Remainder:'%s'" % s.remainder()
    print u"Pass!"

if __name__ == u"__main__":
    main()
