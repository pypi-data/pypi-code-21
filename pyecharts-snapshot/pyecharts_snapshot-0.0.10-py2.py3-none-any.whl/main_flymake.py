import io
import os
import sys
import base64
import subprocess
from PIL import Image


PY2 = sys.version_info[0] == 2

if PY2:
    from StringIO import StringIO as BytesIO
else:
    from io import BytesIO

NOT_SUPPORTED_FILE_TYPE = "Do not support file type %s"
DEFAULT_DELAY = 0.5


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 5:
        raise sys.exit(-1)

    file_name = sys.argv[1]
    if len(sys.argv) == 5:
        output = 'outputs.gif'
        file_type = sys.argv[2]
        delay = float(sys.argv[3])
        interval = int(sys.argv[4])
        make_snapshots(file_name, output, delay, interval)
    else:
        delay = DEFAULT_DELAY
        output = 'output.png'
        if len(sys.argv) >= 3:
            file_type = sys.argv[2]
            if file_type in ['pdf', 'jpeg', 'gif']:
                output = 'output.%s' % file_type
            elif file_type != 'png':
                raise Exception(NOT_SUPPORTED_FILE_TYPE % file_type)
            if len(sys.argv) == 4:
                delay = float(sys.argv[3])  # in seconds
        make_a_snapshot(file_name, output, delay=delay)


def make_snapshots(file_name, output_name, delay, interval):
    file_type = output_name.split('.')[-1]
    # proc = subprocess.Popen(
    #     ['phantomjs',
    #      os.path.join(get_resource_dir('phantomjs'), 'snapshot.js'),
    #      file_name], stdout=subprocess.PIPE)

    # add shell=True and it works on Windows now.

    shell_flag = False
    if sys.platform == 'win32':
        shell_flag = True
    __actual_delay_in_ms = int(delay * 1000)
    proc_params = [
        'phantomjs',
        os.path.join(get_resource_dir('phantomjs'), 'snapshots.js'),
        file_name,
        file_type,
        str(__actual_delay_in_ms),
        str(interval)]
    proc = subprocess.Popen(
        proc_params, stdout=subprocess.PIPE, shell=shell_flag)
    if PY2:
        content = proc.stdout.read()
        content = content.decode('utf-8')
    else:
        content = io.TextIOWrapper(proc.stdout, encoding="utf-8").read()
    images = content.split('---s---')
    image_array = []
    import pdb; pdb.set_trace()
    for image in images:
        if image == '\n':
            continue
        base64_imagedata = image.split(',')[1]
        imagedata = decode_base64(base64_imagedata.encode('utf-8'))
        m = Image.open(BytesIO(imagedata))
        m.load()
        color = (255, 255, 255)
        b = Image.new('RGB', m.size, color)
        b.paste(m, mask=m.split()[3])
        image_array.append(b)
    print(len(image_array))
    image_array[0].save(
        output_name, 'GIF', save_all=True,
        append_images=image_array[1:], duration=2, loop=True)


def make_a_snapshot(file_name, output_name, delay=DEFAULT_DELAY):
    file_type = output_name.split('.')[-1]
    # proc = subprocess.Popen(
    #     ['phantomjs',
    #      os.path.join(get_resource_dir('phantomjs'), 'snapshot.js'),
    #      file_name], stdout=subprocess.PIPE)

    # add shell=True and it works on Windows now.

    shell_flag = False
    if sys.platform == 'win32':
        shell_flag = True
    __actual_delay_in_ms = int(delay * 1000)
    proc_params = [
        'phantomjs',
        os.path.join(get_resource_dir('phantomjs'), 'snapshot.js'),
        file_name,
        file_type,
        str(__actual_delay_in_ms)]
    proc = subprocess.Popen(
        proc_params, stdout=subprocess.PIPE, shell=shell_flag)
    if PY2:
        content = proc.stdout.read()
        content = content.decode('utf-8')
    else:
        content = io.TextIOWrapper(proc.stdout, encoding="utf-8").read()
    base64_imagedata = content.split(',')[1]
    imagedata = decode_base64(base64_imagedata.encode('utf-8'))
    if file_type == 'pdf':
        save_as_pdf(imagedata, output_name)
    elif file_type == 'gif':
        save_as_gif(imagedata, output_name)
    elif file_type in ['png', 'jpeg']:
        save_as_png(imagedata, output_name)
    else:
        raise Exception(NOT_SUPPORTED_FILE_TYPE % file_type)


def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += b'=' * (4 - missing_padding)
    return base64.decodestring(data)


def save_as_png(imagedata, output_name):
    with open(output_name, "wb") as g:
        g.write(imagedata)


def save_as_pdf(imagedata, output_name):
    m = Image.open(BytesIO(imagedata))
    m.load()
    color = (255, 255, 255)
    b = Image.new('RGB', m.size, color)
    b.paste(m, mask=m.split()[3])
    b.save(output_name, 'PDF', quality=100)


def save_as_gif(imagedata, output_name):
    m = Image.open(BytesIO(imagedata))
    m.load()
    color = (255, 255, 255)
    b = Image.new('RGB', m.size, color)
    b.paste(m, mask=m.split()[3])
    b.save(output_name, 'GIF', quality=100)


def get_resource_dir(folder):
    current_path = os.path.dirname(__file__)
    resource_path = os.path.join(current_path, folder)
    return resource_path
