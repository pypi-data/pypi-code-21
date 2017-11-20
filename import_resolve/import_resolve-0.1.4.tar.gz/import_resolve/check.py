import argparse
import os


def make_requirements(modules):
    """
    Makes a requirements.txt file
    :param modules: List of modules
    :return: None
    """
    with open("requirements.txt", "w") as f:
        for module in modules:
            f.write(module)
            f.write("\n")


def get_files(project_folder):
    """
    Recursively goes through the folders to find .py files
    :param project_folder: The project folder which will be checked
    :return: file list containing .py files
    """
    import glob
    os.chdir(project_folder)
    path = "**/**/**/**/**/**/**/**/**/*.py"
    filelist = list(glob.glob(path, recursive=True))
    return filelist


def get_modules(filelist):
    """
    Goes through the python files and extracts the modules
    :param filelist: list of files to be checked
    :return: list of modules used in the files
    """
    str_filelist = " ".join(filelist)
    modulelist = []
    for file in filelist:
        f = open(file, 'r')
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
    modulelist = list(set(modulelist))
    return modulelist


def do_import(modules):
    """
    Tries to import the module and does a pip install
    :param modules: A list of modules
    :return: None
    """
    choice = input("Do you want to download the packages from pip that are not there? (y/n) ").lower()
    for module in modules:
        tokens = 'import ' + module
        try:
            exec(tokens)
        except ImportError:
            print('**"', tokens.replace('import', ''), '" cannot be imported. **')
            if choice == 'y':
                os.system('pip install ' + module)
        else:
            print(tokens.replace('import', ''), 'imported successfully.')
            pass


def main(project_folder):
    """
    Main function resolves the pip errors
    :param project_folder: The project folder which we need to scan
    :return: NULL
    """
    filelist = get_files(project_folder)
    modulelist = get_modules(filelist)
    do_import(modulelist)
    make_requirements(modulelist)


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


# if __name__ == '__main__':
#     main("C:\\Users\\ashis\\Documents\\Py\\Mario-Level-1")
