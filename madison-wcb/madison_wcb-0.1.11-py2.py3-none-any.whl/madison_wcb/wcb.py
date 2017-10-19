import requests
import turtle

### Implementation details

# Global mutable state. Forgive me.
state = {
    'connected_to_bot': False,
    'window': None,
    'turtle': None,
    'distance_traveled': 0,
}

# These measurements are in "steps", which are basically pixels.
WCB_WIDTH = 500
WCB_HEIGHT = 360

SUGGESTED_REINKING_DISTANCE_IN_CM = 48

def _make_cnc_request(endpoint):
    """CNC Server is the way that madison_wcb talks to the WaterColorBot.

    See https://github.com/techninja/cncserver/ for more information.
    """
    if state['connected_to_bot']:
        return requests.get('http://localhost:4242/' + endpoint)


### Public API

def initialize():
    """IMPORTANT: Call this function at the beginning of your program."""
    try:
        requests.get('http://localhost:4242/poll')
        state['connected_to_bot'] = True
    except requests.exceptions.ConnectionError:
        state['connected_to_bot'] = False

    # set up turtle
    state['window'] = turtle.Screen()
    state['window'].setup(width=WCB_WIDTH, height=WCB_HEIGHT)
    state['turtle'] = turtle.Turtle()
    state['turtle'].width(5)

    # set up watercolorbot brush
    brush_up()
    wash_brush()
    park()

def cleanup():
    """IMPORTANT: Call this function at the end of your program."""
    brush_up()
    wash_brush()
    park()

def park():
    """Park the watercolorbot's brush in the top-left corner."""
    _make_cnc_request("park")

def wash_brush():
    """Wash the brush in water."""
    _make_cnc_request("pen.wash")
    state['distance_traveled'] = 0

def get_color(index):
    """Dips the brush in paint.

    Arguments:
        index - an integer between 0 and 7, inclusive. Tells the bot which color you want.
    """
    if index in range(0, 8):
        # Send the turtle to the top-left corner of the window to imitate the position of the WCB's brush.
        state['turtle'].goto(-WCB_WIDTH / 2, -WCB_HEIGHT / 2)

        _make_cnc_request("tool.color./" + str(index))

        # This is the order of the colors in the palette in our classroom's bot; yours may vary!
        colors = ["black", "red", "orange", "yellow", "green", "blue", "purple", "brown"]

        state['turtle'].color(colors[index])
        state['distance_traveled'] = 0

    else:
        print("Color indexes must be between 0 and 7, but you gave me: " + index)

def brush_down():
    """Puts the brush in its "down" position, so that it touches the paper."""
    _make_cnc_request("pen.down")
    state['turtle'].pendown()

    # Wiggle the turtle one step so that it marks a dot on the turtle canvas.
    state['turtle'].forward(1)
    state['turtle'].backward(1)

def brush_up():
    """Puts the brush in its "up" position, so that it doesn't touch the paper."""
    _make_cnc_request("pen.up")
    state['turtle'].penup()

def move_to(x, y):
    """Moves the brush to a particular position.

    Arguments:
        x - a number between -250 and 250.
        y - a number between -180 and 180.
    """
    _make_cnc_request("coord/{0}/{1}".format(x, y))
    state['turtle'].goto(x, y)

def point_in_direction(angle):
    """Points the brush's "turtle" in the direction of the angle specified.

    Arguments:
        angle - a number between 0 and 360.
    """
    # convert angle from regular coordinates to scratch coordinates
    _make_cnc_request("move.absturn./" + str(90 - angle))

    state['turtle'].setheading(angle)

def move_forward(num_steps):
    """Moves the brush forward a few steps in the direction that its "turtle" is facing.

    Arguments:
        num_steps - a number like 20. A bigger number makes the brush move farther.
    """
    _make_cnc_request("move.forward./" + str(num_steps))

    state['turtle'].forward(num_steps)
    state['distance_traveled'] += num_steps

def turn_left(relative_angle):
    """Turns the brush's "turtle" to the left.

    Arguments:
        relative_angle - a number like 10.
            A bigger number makes the turtle turn farther to the left.
    """
    assert int(relative_angle) == relative_angle, "turn_left() only accepts integers, but you gave it " + str(relative_angle)

    _make_cnc_request("move.left./" + str(relative_angle))
    state['turtle'].left(relative_angle)

def turn_right(relative_angle):
    """Turns the brush's "turtle" to the right.

    Arguments:
        relative_angle - a number like 10.
            A bigger number makes the turtle turn farther to the right.
    """
    assert int(relative_angle) == relative_angle, "turn_right() only accepts integers, but you gave it " + str(relative_angle)

    _make_cnc_request("move.right./" + str(relative_angle))
    state['turtle'].right(relative_angle)

def get_position():
    """Returns the brush's current position.

    Return value:
        A list like [-102, 50] representing the brush's current [x, y] position.
    """
    return state['turtle'].position()

def get_x():
    """Returns the brush's current x-coordinate.

    Return value:
        A number between -250 and 250, represnting the brush's current horizontal position.
    """
    return state['turtle'].xcor()

def get_y():
    """Returns the brush's current y-coordinate.

    Return value:
        A number between -180 and 180, representing the brush's current vertical position.
    """
    return state['turtle'].ycor()

def set_reinking_distance(distance_in_cm):
    """Sets the number of centimeters the bot will draw before re-inking the brush with the last used paint.

    Arguments:
        distance_in_cm - an integer representing a number of centimeters.
    """
    _make_cnc_request("penreink/" + str(distance_in_cm))

def get_distance_traveled():
    """Returns a number like 123, representing the distance that the brush has traveled
    since the last time that it was dipped in paint or water.

    NOTE: Only tracks movement triggered by calls to the `move_forward()` function.
    Movement caused by `move_to()` is _not_ recorded.

    This number represents the number of "steps" that the brush has traveled, not the number
    of inches or centimeters; you'll have to do some experimentation on your own to figure
    out e.g. how many centimeters 100 steps is equal to.
    """
    return state['distance_traveled']
