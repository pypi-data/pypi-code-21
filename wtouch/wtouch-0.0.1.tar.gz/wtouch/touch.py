def create_file(file_name):
    try:
        with open(file_name, 'x') as f:
            pass
    except FileExistsError as e:
        pass
