import platform

target = platform.system().lower()

if target == 'windows':
    from .core_windows import install, uninstall

else:
    from .core_linux import install, uninstall
