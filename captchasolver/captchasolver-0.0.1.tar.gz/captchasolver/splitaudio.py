import os
import re
from subprocess import Popen, PIPE
import float_range

from .sox import silence


LETTER_AUDIO_FILE = 'letter.wav'


def file_info(filepath):
    get_info = ['sox', '--info', filepath]
    process = Popen(get_info, stdout=PIPE, encoding='utf-8')
    info, err = process.communicate()
    return info.splitlines()


def split_letters(audio_file, duration, threshold, output=LETTER_AUDIO_FILE,
                  verbosity=2):
    threshold = str(threshold) + '%'
    cmd = ['sox', f'-V{verbosity}', audio_file, output,
           f'silence 1 {duration} {threshold} 1 {duration} {threshold}',
           ': newfile', ': restart']
    os.system(cmd)


def count_letters(letter_audio_file):
    name, extension = letter_audio_file.split('.')
    count = len([i for i in os.listdir() if i.startswith(name)])
    return count


def assert_minimum_size(letters, path):
    MIN_SIZE = 2500
    MAX_SIZE = 11000
    SOUND_ERROR = 44
    valid_letters_count = 0

    for letter in letters:
        size = os.path.getsize(letter)
        if size == SOUND_ERROR:
            os.remove(letter)
            continue
        if MIN_SIZE < size < MAX_SIZE and valid_letters_count < 6:
            valid_letters_count += 1
        else:
            return False

    return valid_letters_count == 6


def validate_results(path='.'):
    pattern = '^letter\d{3}\.wav$'
    letters = [os.path.join(path, fn)
               for fn in os.listdir(path)
               if re.match(pattern, fn)]
    return assert_minimum_size(letters, path)


def clean_up(letter_audio_file, path='.'):
    pattern = '^letter\d{3}\.wav$'
    letters = [os.path.join(path, fn)
               for fn in os.listdir(path)
               if re.match(pattern, fn)]
    for i in letters:
        os.remove(i)


def get_captchas():
    pattern = '^captcha_\d{4}\.wav$'
    cwd = os.getcwd()
    captchas = [os.path.join(cwd, i) for i in os.listdir()
                if re.match(pattern, i)]
    return captchas


def process_capthcas(captchas, duration, threshold, target=0):
    conta_validos = 0
    performance = 0
    for n, captcha in enumerate(captchas):
        split_letters(captcha, duration, threshold)
        is_valid = validate_results(LETTER_AUDIO_FILE)
        if is_valid:
            conta_validos += 1

        performance = conta_validos / len(captchas)
        clean_up(LETTER_AUDIO_FILE)

    print('duration:', '{0:.4f}'.format(duration),
          'threshold:', '{0:.4f}'.format(threshold),
          '| Performance:', '{0:.4f}'.format(performance),
          'Target:', '{0:.4f}'.format(target))

    return performance


def letters_audio():
    letters = []
    pattern = '^letter\d{3}\.wav$'
    files = [fn for fn in os.listdir() if re.match(pattern, fn)]
    for i in sorted(files):
        with open(i, 'rb') as f:
            audio = f.read()
        letters.append(audio)
    return letters


def solve_captcha(captcha, clean=True,
                  duration={'min': 0, 'max': 0.175, 'step': 0.025},
                  threshold={'min': 6.9, 'max': 13.10, 'step': 0.10},
                  temp_dir=None):

    MIN_DURATION = duration['min']
    STEP_DURATION = duration['step']
    MAX_DURATION = duration['max'] + STEP_DURATION

    MIN_THRESHOLD = threshold['min']
    STEP_THRESHOLD = threshold['step']
    MAX_THRESHOLD = threshold['max'] + STEP_THRESHOLD

    for t in float_range.range(
            MIN_THRESHOLD, MAX_THRESHOLD, STEP_THRESHOLD):
        for d in float_range.range(
                MIN_DURATION, MAX_DURATION, STEP_DURATION):
            solved = False
            letter_count = silence(captcha, d, t, cwd=temp_dir)
            if letter_count >= 6:
                solved = validate_results(temp_dir)
            if solved:
                return (d, t), letters_audio()
                if clean:
                    clean_up(LETTER_AUDIO_FILE)
            clean_up(LETTER_AUDIO_FILE, temp_dir)
    return False


def save_result(resultado, log='log.txt'):
    with open(log, 'a') as f:
        f.write('{0:.4f}'.format(resultado[0]) + ';' +
                '{0:.4f}'.format(resultado[1]) + ';' + '\n')
