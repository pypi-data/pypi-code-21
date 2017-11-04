# __init__.py

from thonny.globals import get_workbench
from tkinter.messagebox import showerror
from tkinter.messagebox import showinfo

import traceback
import os
import uflash

#----- FLASH HEX FILE CODE FROM THONNY-MICROBIT -------------------------------

def flash_current_script_enabled():
    """Return false if flashing is not possible."""
    #TODO
    return True

def flash_io_runtime():
    """Flashes MicroPython with the default IO .hex"""
    try:
        microbit_path = uflash.find_microbit()
        if microbit_path:
            _BITIO_RUNTIME = os.path.join(os.path.dirname(__file__), "res", "bitio.hex")
            uflash.flash(path_to_runtime=_BITIO_RUNTIME)
            showinfo("Flashing micro:bit", "Flashing the I/O .hex to micro:bit")
    except Exception:
        error_msg = traceback.format_exc(0)+'\n'
        showerror("Error", error_msg)

#----- THONNY PLUGIN CODE ADAPTED FROM THONNY-MICROBIT --------------------------

def load_plugin():
    """Adds flash button on GUI and commands under Tools menu."""
    image_path = os.path.join(os.path.dirname(__file__), "res", "run.flash_io.gif")
    get_workbench().add_command("flashmicrobitio", "tools", "Flash I/O .hex to BBC micro:bit",
                                flash_io_runtime,
                                flash_current_script_enabled,
                                default_sequence="<Control-i>",
                                group=120,
                                image_filename=image_path,
                                include_in_toolbar=True)
