from madison_wcb.wcb import *


def box():
    initialize()

    get_color(0)

    move_to(100, 0)
    point_in_direction(-90)
    brush_down()

    for i in range(360):
        move_forward(2)
        turn_right(1)

    cleanup()
    input("Done! Press Enter to close the program.")


if __name__ == "__main__":
    box()
