PIP_CMD = 'pip --isolated --no-cache-dir'

_PIP_DOWNLOAD_CMD = PIP_CMD + ' download --dest "{}"'
PIP_DOWNLOAD_SRC_CMD = PIP_CMD + ' download --dest "{}" -e "{}"'
PIP_DOWNLOAD_REQ_CMD = PIP_CMD + ' download --dest "{}" -r "{}"'

PIP_INSTALL_CMD = (
    PIP_CMD +
    ' install --no-index --find-links "{0}" --ignore-installed "{0}"/*')
