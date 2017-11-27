import sys
import os
import platform

import autest.api as api

def IsPlatform(self, *lst):
    return self.Condition(
        lambda: sys.platform.lower() in lst or platform.system(
        ).lower() in lst or os.name.lower() in lst,
        'Platform must be one of {0}, reported value was "{1}" or "{2}"'.
        format(lst, platform.system().lower(), os.name),
        True,
        'Platform must not be one of {0}, reported value was "{1}" or "{2}"'.
        format(lst, platform.system().lower(), os.name), )

def IsNotPlatform(self, *lst):
    return self.Condition(
        lambda: sys.platform.lower() in lst or platform.system(
        ).lower() in lst or os.name.lower() in lst,
        'Platform must not be one of {0}, reported value was "{1}" or "{2}"'.
        format(lst, platform.system().lower(), os.name),
        False,
        'Platform must be one of {0}, reported value was "{1}" or "{2}"'.
        format(lst, platform.system().lower(), os.name), )


api.ExtendCondition(IsPlatform)
api.ExtendCondition(IsNotPlatform)