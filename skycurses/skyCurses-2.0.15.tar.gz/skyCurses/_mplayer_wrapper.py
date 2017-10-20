from mplayer import Player as Player_old
import sys
import subprocess


class Player(Player_old):
    def spawn(self):
        if self.is_alive():
            return
        args = [self.exec_path]
        args.extend(self._args)
        # Start the MPlayer process (unbuffered)
        self._proc = subprocess.Popen(args, stdin=subprocess.PIPE,
            stdout=self._stdout._handle, stderr=self._stderr._handle,
            close_fds=(sys.platform != 'win32'))
        if self._proc.stdout is not None:
            self._stdout._attach(self._proc.stdout)
        if self._proc.stderr is not None:
            self._stderr._attach(self._proc.stderr)
