import sftoolboxqt.engineinterface
# make a qtgui available
_qt_system = None

if not _qt_system:
    try:
        import PySide

        _qt_system = 'PySide'
    except ImportError:
        pass

if not _qt_system:
    try:
        import PySide2

        _qt_system = 'PySide2'
    except ImportError:
        pass

if _qt_system == 'PySide':
    import sftoolboxqt.qtguipyside as qtgui
elif _qt_system == 'PySide2':
    import sftoolboxqt.qtguipyside2 as qtgui
else:
    raise ImportError

# make qtcore available
if _qt_system == 'PySide':
    from PySide import QtCore as qtcore
elif _qt_system == 'PySide2':
    from PySide2 import QtCore as qtcore
else:
    raise ImportError
assert qtcore
assert qtgui

engine = sftoolboxqt.engineinterface.Engine()
