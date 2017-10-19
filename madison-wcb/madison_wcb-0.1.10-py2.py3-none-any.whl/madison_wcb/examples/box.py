from madison_wcb.wcb import *


def box():
    initialize()

    get_color(2)

    move_to(-50, 50)
    point_in_direction(0)
    brush_down()

    for i in range(4):
        move_forward(100)
        turn_right(90)

    cleanup()
    input("Done! Press Enter to close the program.")


if __name__ == "__main__":
    box()
