from madison_wcb import *


def box():
    initialize()

    move_to(-10, 10)
    point_in_direction(0)
    brush_down()

    for i in range(4):
        move_forward(20)
        turn_right(90)

    cleanup()
    input("Done! Press Enter to close the program.")


if __name__ == "__main__":
    box()
