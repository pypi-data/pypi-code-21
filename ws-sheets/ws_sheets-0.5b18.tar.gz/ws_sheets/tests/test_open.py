
import ws_sheets

class TestOpen:

    def test_helper(self, settings):
        b = ws_sheets.Book(settings)
        
        s = b.sheets['0']
        
        b.set_cell('0', 0, 0, "open('a.txt')")
        
        print(s.cells.cells[0, 0].value)

        b.set_cell('0', 0, 0, "open('a.txt', 'w').write('hello world')")
        
        print(s.cells.cells[0, 0].value)

        b.set_cell('0', 0, 0, "open('a.txt', 'r').read()")
        
        print(s.cells.cells[0, 0].value)



