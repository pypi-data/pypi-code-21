import argparse


def main(project_folder):
    """
    Main function resolves the pip errors
    :param project_folder: The project folder which we need to scan
    :return: NULL
    """
    try:
        import sys, os
        import __main__ as main
        import glob
    except ImportError:
        print("Please do a pip install glob")
    # this part scans for python files recursively
    os.chdir(project_folder)
    path = "**/**/**/**/**/**/**/**/**/*.py"
    filelist = list(glob.glob(path, recursive=True))
    str_filelist = " ".join(filelist)
    modulelist = list()  # list of modules to be checked for
    for file in filelist:
        f = open(file, 'r')
        if file.endswith(main.__file__):
            continue
        print('evaluating file: ', file)
        content = f.readlines()
        for line in content:
            tokens = line.strip()
            if tokens.startswith('import') or tokens.startswith('from'):
                try:
                    tokens = tokens.replace(',', '\n')
                    tokens = tokens.split()
                    try:
                        if line[5] == '.':
                            continue
                    except IndexError:
                        pass
                    if 'as' in tokens:
                        tokens.remove(tokens[tokens.index('as') + 1])
                    if 'from' in tokens:
                        tokens.remove(tokens[tokens.index('from') + 3])
                    if 'import' in tokens:
                        tokens.remove('import')
                    if 'as' in tokens:
                        tokens.remove('as')
                    if 'from' in tokens:
                        tokens.remove('from')
                    for modname in tokens:
                        py = modname + ".py"
                        if "." not in modname and py not in str_filelist:
                            modulelist.append(modname)
                except ValueError:
                    pass
        f.close()

    # removing duplicates from the list of modules obtained
    modulelist = list(set(modulelist))
    print("Modules Found")
    print(modulelist)
    choice = input("Do you wish to download any modules that are unavailable (requires pip)? (y/n) ").lower()
    print()
    for modulename in modulelist:
        tokens = 'import ' + modulename
        try:
            exec(tokens)
        except ImportError:
            print('**"', tokens.replace('import', ''), '" cannot be imported. **')
            if choice == 'y':
                os.system('pip install ' + tokens.replace('import', ''))
        else:
            print(tokens.replace('import', ''), 'imported successfully.')
            pass


def argParser():
    """
    The main CLI function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("project_folder", help="The location of your project",
                        type=str)
    args = parser.parse_args()
    try:
        # print(args)
        main(args.project_folder)
    except Exception as e:
        print(e)
