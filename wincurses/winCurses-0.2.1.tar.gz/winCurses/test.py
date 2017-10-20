import unittest
from Win import *
from WDisp import *
from WInput import *
from WNotif import *
from WList import *
from time import sleep

def winCursesWrap(f):
    def wrapper(self):
        root = Win()
        root.clear(True)
        res = f(self, root)
        del root
        return(res)

    return(wrapper)



class TestWDispWindow(unittest.TestCase):
    @winCursesWrap
    def test_creation(self, root):
        big_win  = WDisp(root, None, None, 0, ['*'] * 8)
        main_win = WDisp(root, Coord(0,0), Coord(0.7, 0.7, True), 2, [0])
        sec_win  = WDisp(root, Coord(0.5, 0.5, True), Coord(0.5, 0.5, True), 1, [0])
        root.refresh(True)
        sleep(2)

    @winCursesWrap
    def test_writing(self, root):
        main_win = WDisp(root, None, Coord(0.6, 0.6, True), 0, [0])
        main_win.disp("azaza")
        sleep(1)
        main_win.disp("azaza2")
        sleep(2)

    @winCursesWrap
    def test_tagged_disp(self, root):
        main_win = WDisp(root, Coord(0,0), Coord(5, 1, (False, True)), 0, [0])
        main_win.disp('<cr>H</cr><cy>e</cy><cg>l</cg><cc>l</cc><cb>o</cb> <b><cm>W</cm><cb>o</cb><cc>r</cc><cg>l</cg><cy>d</cy> <cr>!</cr></b>')
        sleep(1)
        main_win.disp('<u>Toast</u>')
        sleep(1)
        main_win.disp('<b>Hello<cy>FaunJTM</cy></b><cr>RedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTM</cr> <u>END</u>')
        sleep(2)

    @winCursesWrap
    def test_line_overflow(self, root):
        main_win = WDisp(root, Coord(0,0), Coord(5, 50, False), 0, [0])
        main_win.disp('<b>Hello<cy>FaunJTM</cy></b><cr>RedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTMRedJTM</cr> <u>END</u>')
        sleep(2)

    @winCursesWrap
    def test_history(self, root):
        main_win = WDisp(root, Coord(0,0), Coord(5, 50, False), 0, [0])
        for i in range(100):
            main_win.disp("azaza lorem ipsum %d" % (i))
        sleep(2)
        main_win.change_offset(-4)
        sleep(2)
        main_win.change_offset(2)
        sleep(2)
        main_win.change_offset(0, True)
        sleep(2)
        main_win.change_offset(4)
        sleep(2)
        main_win.change_offset(-2)
        sleep(2)
        main_win.change_offset(-6)
        sleep(2)

    @winCursesWrap
    def test_flood(self, root):
        main_win = WDisp(root, Coord(0,0), Coord(5, 50, False), 0, [0])
        text     = ""
        for i in range(100):
            for j in range(10):
                text += str(j)
        main_win.disp(text)
        sleep(2)


#class TestWNotifWindow(unittest.TestCase):
#    @winCursesWrap
#    def test_heigh(self, root):
#        notif_win = WNotif(root, Coord(0,0), Coord(8, 50), 0, [0])
#        assert(notif_win.dim.y == 1)
#
#    @winCursesWrap
#    def test_simple(self, root):
#        notif_win = WNotif(root, Coord(0,0), Coord(1, 50), 0, [0])
#        notif_win.disp("azaza")
#        sleep(2)
#        notif_win.reset()
#        sleep(1)

#class TestWInputWindow(unittest.TestCase):
#    @winCursesWrap
#    def test_simple(self, root):
#        disp_win  = WDisp(root, Coord(0,0), Coord(4, 50), 0, [0])
#        input_win = WInput(root, Coord(4, 0), Coord(8, 50), 0, [0],
#                on_return=lambda x : disp_win.disp(x),
#                on_spec_key=lambda x : disp_win.disp('<cm>SPECIAL KEY ' + x + '</cm>'),
#                on_typing=lambda x : disp_win.disp('<cg>on</cg>' if x else '<cr>off</cr>')
#                )
#        input_win.start()

#class TestWListWindow(unittest.TestCase):
#    def test_yolo(self):
#        print("yolo")
#
#    @winCursesWrap
#    def test_simple(self, root):
#        wlist_win = WList(root, Coord(2,3), Coord(5,10))
#        wlist_win.append('1')
#        sleep(2)
#        wlist_win.append('2')
#        sleep(2) 
#        wlist_win.append('3')
#        sleep(2)
#        wlist_win.remove('2')
#        sleep(2)
#        wlist_win.append('4')
#        sleep(2)
#        del wlist_win[1]
#        sleep(2)

if __name__ == "__main__":
    unittest.main()
