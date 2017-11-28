class StringParser:
    def __init__( self, text: str ):
        self.text = text
        self.cursor = 0
    
    
    def read_char( self ):
        return self.read_text( 1 )
    
    
    def read_text( self, length: int ):
        result = self.text[ self.cursor:self.cursor + length ]
        self.cursor += length
        return result
    
    
    def read_to( self, find: str ):
        start = self.cursor
        end = self.text.find( find, start )
        
        if end == -1:
            end = len( self.text )
            
        self.cursor = end
        
        return self.text[ start:end ]
    
    
    def read_past( self, find: str ):
        result = self.read_to( find )
        self.cursor += len( find )
        return result
    
    
    def read_all( self ):
        return self.read_text( len( self.text ) - self.cursor )
    
    
    def end( self ):
        return self.cursor >= len( self.text )


def string_parser_unit_test():
    TEST_STRING = "Once I had a lemon."
    
    parser = StringParser( TEST_STRING )
    
    # |O|nce I had a lemon.
    x = parser.read_char()
    print(x)
    assert x == "O", "[{}]".format(x)
    
    # O|nce |I had a lemon.
    x = parser.read_text( 4 )
    print(x)
    assert x == "nce ", "[{}]".format(x)
    
    # Once |I| had a lemon.
    x = parser.read_to( " " )
    print(x)
    assert x == "I", "[{}]".format(x)
    
    # Once I| |had a lemon.
    x = parser.read_char()
    print(x)
    assert x == " ", "[{}]".format(x)
    
    # Once I |had| |a lemon.
    x = parser.read_past( " " )
    print(x)
    assert x == "had"
    
    # Once I had |a| lemon.
    x = parser.read_char()
    print(x)
    assert x == "a"
    
    assert not parser.end()
    
    # Once I had a| lemon.|
    x = parser.read_all()
    print(x)
    assert x == " lemon.", "[{}]".format(x)
    
    assert parser.end()
