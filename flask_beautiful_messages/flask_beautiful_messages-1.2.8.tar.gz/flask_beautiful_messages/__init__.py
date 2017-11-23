from . helper import *

BLUE_BUTTON_STYLE = """
    .btn {
        background: #3498db;
        background-image: -webkit-linear-gradient(top, #3498db, #2980b9);
        background-image: -moz-linear-gradient(top, #3498db, #2980b9);
        background-image: -ms-linear-gradient(top, #3498db, #2980b9);
        background-image: -o-linear-gradient(top, #3498db, #2980b9);
        background-image: linear-gradient(to bottom, #3498db, #2980b9);
        -webkit-border-radius: 28;
        -moz-border-radius: 28;
        border-radius: 28px;
        font-family: Arial;
        color: #ffffff;
        border: solid #1f628d 3px;
        text-decoration: none;
    }

    .btn:hover {
        background: #3cb0fd;
        background-image: -webkit-linear-gradient(top, #3cb0fd, #3498db);
        background-image: -moz-linear-gradient(top, #3cb0fd, #3498db);
        background-image: -ms-linear-gradient(top, #3cb0fd, #3498db);
        background-image: -o-linear-gradient(top, #3cb0fd, #3498db);
        background-image: linear-gradient(to bottom, #3cb0fd, #3498db);
        text-decoration: none;
        cursor:pointer;
    }
"""

styles = {
    'bubble_gum':{
        'background_image': "/static/images/blue-bubbles.jpg",
        'main_wrapper_color': 'rgba(0, 0, 255, 0.65)',
        'message_container_color': 'pink',
        'button_style':BLUE_BUTTON_STYLE,
    },
    'serious': {
        'background_image': "None",
        'main_wrapper_color': 'rgba(0, 0, 255, 0.65)',
        'message_container_color': 'pink',
        'button_style': BLUE_BUTTON_STYLE,
    },

}