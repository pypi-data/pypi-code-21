from helpers.config_manager import get_cfg, set_cfg
from helpers.logo import logo
from helpers.compose import paint

def print_worklist():
    cfg = get_cfg()
    if 'worklist' in cfg:
        wl = cfg['worklist']
        if len(wl) > 0:
            logo()
            print("Here's what Reactjo just did for you")
            for item in wl:
                print(paint('- ' + item, 'green'))

            print("Enjoy :-)")
            print(" ")

        cfg['worklist'] = []
        set_cfg(cfg)

def worklist(string, prev_path = None):
    # Solves issues with finding config.json after changing dirs
    if prev_path:
        next_path = os.getcwd()
        os.chdir(prev_path)

    cfg = get_cfg()

    # Create worklist if necessary. Should never be necessary.
    if not 'worklist' in cfg:
        cfg['worklist'] = []

    # Add worklist entry
    cfg['worklist'].append(string)
    set_cfg(cfg)

    if prev_path:
        os.chdir(next_path)
