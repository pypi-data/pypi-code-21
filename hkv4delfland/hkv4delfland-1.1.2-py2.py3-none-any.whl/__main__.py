import fire
from hkv4delfland.io.bui import __bui_class
from hkv4delfland.io.his import __his_class
from hkv4delfland.core.waterlevelstat import __waterlevelstat_class
from hkv4delfland.core.plausibility import __plausibility_class


# initiate class for .bui-files
__bui = __bui_class()
read_bui = __bui.read_bui

# initiate class for .his-files
read_his = __his_class()

# initiate class for waterlevelstats
waterlevelstat = __waterlevelstat_class()

# initiate class for plausibilitychecker
plausibility = __plausibility_class()

if __name__ == '__main__':
  fire.Fire()