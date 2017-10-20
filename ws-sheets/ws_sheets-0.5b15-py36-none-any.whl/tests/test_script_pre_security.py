import numpy
import ws_sheets
import ws_sheets.exception
import ws_sheets.tests.conf

def test_script_pre_security(settings):
    b = ws_sheets.Book(settings)

    b.set_script_pre('book.do_all')
    
    b.do_all()
    
    print('output')
    print(b.script_pre.output)
    print('exc')
    print(repr(b.script_pre.exec_exc))
    print(repr(b.script_pre.exec_exc.__class__))
    
    assert isinstance(b.script_pre.exec_exc, ws_sheets.exception.NotAllowedError)

    b.set_script_pre('getattr(book,\'do_all\')')
    
    b.do_all()
    
    print('output')
    print(b.script_pre.output)
    print('exc')
    print(repr(b.script_pre.exec_exc))
    print(repr(b.script_pre.exec_exc.__class__))
    
    assert isinstance(b.script_pre.exec_exc,
        ws_sheets.exception.NotAllowedError)
    
    
    b.set_script_pre('object.__getattribute__(book,\'do_all\')')

    b.do_all()
    
    print('output')
    print(b.script_pre.output)
    print('exc')
    print(repr(b.script_pre.exec_exc))
    print(repr(b.script_pre.exec_exc.__class__))
    
    assert isinstance(b.script_pre.exec_exc,
        ws_sheets.exception.NotAllowedError)
    
    


