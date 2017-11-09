import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED
from glob import glob
import os
import pickle
import re
import shutil
import signal
import sys
import tempfile

import psutil

from .features import extract_audio_file_features
from .splitaudio import solve_captcha

# pickled k-Nearest Neighbors (KNN) Model
KNN_MODEL = os.path.join(os.path.split(__file__)[0], 'data', 'model.pkl')


def load_model(filename=KNN_MODEL):
    with open(filename, 'rb') as f:
        model = pickle.loads(f.read())
    return model


def resolve_captcha(letras):
    knn = load_model()
    captcha = ''
    for letra in letras:
        features = extract_audio_file_features(letra)
        prediction = knn.predict(features)
        captcha = ''.join([captcha, prediction[0]])
    return captcha


def solver(audio_file, min_threshold, max_threshold):
    filename = os.path.basename(audio_file)

    temp_dir = tempfile.TemporaryDirectory()
    shutil.copyfile(os.path.abspath(audio_file),
                    os.path.join(temp_dir.name, filename))


    threshold = {'min': min_threshold, 'max': max_threshold, 'step': 0.10}
    if solve_captcha(filename, threshold=threshold, clean=False,
                     temp_dir=temp_dir.name):
        caracteres = sorted(glob(os.path.join(temp_dir.name, 'letter*.wav')))
        return resolve_captcha(caracteres)
    else:
        return False


def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)


def get_tasks(n, audiofile, start=6.9, end=13.2):
    tasks = []
    size = (end - start) / n
    for _ in range(n):
        max_threshold = start + size
        tasks.append((audiofile, start, max_threshold))
        start = max_threshold
    return tasks


def solve(audiofile, processes=4):
    tasks = get_tasks(processes, audiofile)
    pool = ProcessPoolExecutor(processes)
    fs = [pool.submit(solver, *i) for i in tasks]

    solution = False
    while not solution:
        done, not_done = concurrent.futures.wait(fs, timeout=None,
                                                 return_when=FIRST_COMPLETED)
        for task in done:
            result = task.result()
            if result is not False:
                solution = result
                break

    pool.shutdown(wait=False)
    kill_child_processes(os.getpid())

    return solution


if __name__ == '__main__':
    audiofile = sys.argv[1]
    captcha = solve(audiofile)
    print('Captcha:', captcha)
