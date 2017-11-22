import unittest


class SpecialStrings_test( unittest.TestCase ):
    def test_special_strings( self ):
        from neocommand.helpers.special_types import TNodeUid
        from mhelper import Filename

        # NODE UID
        
        spam_eggs_beans = TNodeUid[ "spam" ][ "eggs" ]( "beans" )
        
        self.assertTrue( spam_eggs_beans == "beans")
        self.assertTrue(spam_eggs_beans != "lemon")
        self.assertTrue(isinstance( spam_eggs_beans, str ))
        self.assertTrue( isinstance( spam_eggs_beans, TNodeUid ) )
        self.assertTrue( isinstance( spam_eggs_beans, TNodeUid[ "spam" ] ) )
        self.assertTrue( isinstance( spam_eggs_beans, TNodeUid[ "eggs" ] ) )
        self.assertTrue( not isinstance( spam_eggs_beans, TNodeUid[ "oranges" ] ) )
        
        
        # FILENAME
        
        file_name_type = Filename[ ".txt" ]
        file_name = file_name_type( "/hello" )
        
        # Filename should be complete
        self.assertTrue(file_name == "/hello.txt") 
        self.assertTrue(file_name != "/hello.csv")
        self.assertTrue(file_name != "/hello")
        
        # Filename type should be correct
        self.assertTrue(isinstance( file_name, str ))
        self.assertTrue(isinstance( file_name, Filename ))
        self.assertTrue(isinstance( file_name, Filename[ ".txt" ] ))
        self.assertTrue(isinstance( file_name, file_name_type ))
        self.assertTrue(not isinstance( file_name, Filename[ ".csv" ] ))
        
        # IExtension should be gettable
        self.assertTrue(file_name.extension == ".txt") 
        self.assertTrue(file_name.extension != ".csv")
        
        # Type should have extension
        self.assertTrue(file_name.type_extension == ".txt") 
        self.assertTrue(file_name.type_extension != ".csv")
        self.assertTrue(file_name_type.type_extension == ".txt") 
        self.assertTrue(file_name_type.type_extension != ".csv")
        
        # Type should be sub-classed correctly
        self.assertTrue(issubclass( file_name_type, Filename ))
        self.assertTrue(issubclass( file_name_type, str ))
        self.assertTrue(issubclass( file_name_type, Filename[ ".txt" ] ))
        self.assertTrue(not issubclass( file_name_type, Filename[ ".csv" ] ))




