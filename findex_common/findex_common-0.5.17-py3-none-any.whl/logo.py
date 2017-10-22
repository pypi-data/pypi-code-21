# This code has been 'borrowed' Cuckoo Sandbox
#     https://github.com/cuckoosandbox/cuckoo/
# Credits go to @jbremer (Jurriaan Bremer) and the Cuckoo team

import sys
import random

from findex_common.colors import color, yellow


def logo(version):
    """Cuckoo asciiarts.
    :param version: version string
    @return: asciiarts array.
    """
    logos = []

    logos.append("""
  ___________.___ _______  ________  _______________  ___
  \_   _____/|   |\      \ \______ \ \_   _____/\   \/  /
   |    __)  |   |/   |   \ |    |  \ |    __)_  \     /
   |     \   |   /    |    \|    `   \|        \ /     \\
   \___  /   |___\____|__  /_______  /_______  //___/\  \\
       \/                \/        \/        \/       \_/""")

    logos.append("""
  _____ ___ _   _ ____  _______  __
 |  ___|_ _| \ | |  _ \| ____\ \/ /
 | |_   | ||  \| | | | |  _|  \  / 
 |  _|  | || |\  | |_| | |___ /  \ 
 | |   |___|_| \_|____/|_____/_/\_\\
 |_|-gui ~~~~~~~~~~~~~~~~~~~~~~~~~~
    """)

    # http://www.ad.nl/amersfoort/ransuil-nieuwe-bewoner-van-boom-in-amersfoort~aee12de2/
    logos.append("""
   __________
  / ___  ___ \\
 / / @ \/ @ \ \   ~gino the ghetto owl~
 \ \___/\___/ /\       ~sees all~
  \____\/____/||
  /     /\\\\\\\\\//
  |     |\\\\\\\\\\\\
  \      \\\\\\\\\\\\
   \______/\\\\\\\\
    _||_||_
     -- --""")

    logos.append("""
    █████▒██▓ ███▄    █ ▓█████▄ ▓█████ ▒██   ██▒
  ▓██   ▒▓██▒ ██ ▀█   █ ▒██▀ ██▌▓█   ▀ ▒▒ █ █ ▒░
  ▒████ ░▒██▒▓██  ▀█ ██▒░██   █▌▒███   ░░  █   ░
  ░▓█▒  ░░██░▓██▒  ▐▌██▒░▓█▄   ▌▒▓█  ▄  ░ █ █ ▒
  ░▒█░   ░██░▒██░   ▓██░░▒████▓ ░▒████▒▒██▒ ▒██▒
   ▒ ░   ░▓  ░ ▒░   ▒ ▒  ▒▒▓  ▒ ░░ ▒░ ░▒▒ ░ ░▓ ░
   ░      ▒ ░░ ░░   ░ ▒░ ░ ▒  ▒  ░ ░  ░░░   ░▒ ░
   ░ ░    ▒ ░   ░   ░ ░  ░ ░  ░    ░    ░    ░
          ░           ░    ░       ░  ░ ░    ░
                      ░""")

    logos.append("""
 ________ ___  ________   ________  _______      ___    ___
|\  _____\\\\  \|\   ___  \|\   ___ \|\  ___ \    |\  \  /  /|
\ \  \__/\ \  \ \  \\\\ \  \ \  \_|\ \ \   __/|   \ \  \/  / /
 \ \   __\\\\ \  \ \  \\\\ \  \ \  \ \\\\ \ \  \_|/__  \ \    / /
  \ \  \_| \ \  \ \  \\\\ \  \ \  \_\\\\ \ \  \_|\ \  /     \/
   \ \__\   \ \__\ \__\\\\ \__\ \_______\ \_______\/  /\   \\
    \|__|    \|__|\|__| \|__|\|_______|\|_______/__/ /\ __\\
                                                |__|/ \|__|""")

    logos.append("""
             .                     ..                               ..
   oec :    @88>                 dF                       .H88x.  :~)88:
  @88888    %8P      u.    u.   '88bu.                   x888888X ~:8888
  8"*88%     .     x@88k u@88c. '*88888bu        .u     ~   "8888X  %88"
  8b.      .@88u  ^"8888""8888"   ^"*8888N    ud8888.        X8888
 u888888> ''888E`   8888  888R   beWE "888L :888'8888.    .xxX8888xxxd>
  8888R     888E    8888  888R   888E  888E d888 '88%"   :88888888888"
  8888P     888E    8888  888R   888E  888E 8888.+"      ~   '8888
  *888>     888E    8888  888R   888E  888F 8888L       xx.  X8888:    .
  4888      888&   "*88*" 8888" .888N..888  '8888c. .+ X888  X88888x.x"
  '888      R888"    ""   'Y"    `"888*""    "88888%   X88% : '%8888"
   88R       ""                     ""         "YP'     "*=~    `""
   88>
   48
   '8""")

    logos.append("""
  ▄████  ▄█    ▄   ██▄   ▄███▄      ▄
  █▀   ▀ ██     █  █  █  █▀   ▀ ▀▄   █
  █▀▀    ██ ██   █ █   █ ██▄▄     █ ▀
  █      ▐█ █ █  █ █  █  █▄   ▄▀ ▄ █
   █      ▐ █  █ █ ███▀  ▀███▀  █   ▀▄
    ▀       █   ██               ▀""")

    subtitles = [
        "Index all teh things!",
        "wo0two0t!", "You know, for searching!"
        ""
    ]
    print(color(random.choice(logos), random.randrange(31, 37)))
    print(" \"%s\"" % random.choice(subtitles))
    print()
    print(" Findex-GUI %s" % yellow(version))
    print(" https://github.com/skftn/findex-gui")
    print(" Sander Ferdinand")
    print(" CedSys (c) 2014-2017")
    print()
    sys.stdout.flush()
