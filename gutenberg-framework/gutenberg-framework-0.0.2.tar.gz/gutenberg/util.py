import dateutil.parser as parser;

def isDate(string):
    try:
        parser.parse(string);
        return True;
    except ValueError:
        return False;
