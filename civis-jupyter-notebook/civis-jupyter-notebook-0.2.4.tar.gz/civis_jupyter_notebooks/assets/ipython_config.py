c = get_config() # noqa

c.InteractiveShellApp.extensions.append('civis_jupyter_ext')
c.InteractiveShellApp.exec_files.append('civis_client_config.py')
