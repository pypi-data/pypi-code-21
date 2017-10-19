from madison_wcb.wcb import *


def spiky_circle():
    initialize()

    get_color(0)

    move_to(100, 0)
    point_in_direction(180)
    brush_down()

    for i in range(15):
        move_forward(200)
        turn_right(192)

    cleanup()
    input("Done! Press Enter to close the program.")


if __name__ == "__main__":
    spiky_circle()
