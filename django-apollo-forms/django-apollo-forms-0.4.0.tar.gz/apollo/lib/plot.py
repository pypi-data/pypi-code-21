import matplotlib.pyplot as plt


def draw_rectangle(top_left, bottom_right):
    min_x, min_y, max_x, max_y = top_left + bottom_right

    plt.plot(
        [min_x, max_x, max_x, min_x, min_x],
        [max_y, max_y, min_y, min_y, max_y],
    )


def show():
    plt.show()
