import simpleaudio
from threading import Thread

CHUNK_SIZE = 1024


class Sound:
    def __init__(self, path):
        """ Wrapper for sound playing

        path -- WAV file path
        """
        self.playing = False
        self._sound  = simpleaudio.WaveObject.from_wave_file(path)

    def __del__(self):
        pass

    def play(self):
        """ Plays the sound in a different thread (non-blocking) """
        if not self.playing:
            Thread(target=self._play_sound, daemon=True).start()
        return(self)

    def play_wait(self):
        """ Plays the sound in the main thread (blocking) """
        self._play_sound()

    def _play_sound(self):
        self.playing = True
        self._sound.play().wait_done()
        self.playing = False

    def close(self):
        pass
