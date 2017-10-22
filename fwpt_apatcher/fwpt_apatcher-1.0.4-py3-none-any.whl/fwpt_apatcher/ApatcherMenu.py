# модуль для работ с консольным меню по редактированию списка файлов
def show_menu():
    print("\t1. Add file;")
    print("\t2. Delete file;")
    print("\t3. Accept;")
    print("\t4. Exit;")

    choice = input("\t\t:")
    if choice not in {"1", "2", "3", "4"}:
        print("Error in menu item")
        exit(0)

    if choice == "4":
        print("Exit -> True")
        exit(0)

    return int(choice)


def print_list(lmass, name=""):
    print("\nEditing list of " + name + ": ")
    for i in range(0, len(lmass)):
        print(str(i) + ". " + lmass[i])


def edit_list(lmass=None, action=0):
    if lmass is None:
        lmass = []
    if action == 1:
        # получим новый файл
        new_filename = input("Enter file name: ")
        lmass.append(new_filename)
        return lmass
    elif action == 2:
        del_num = input("Enter file number in list: ")
        del lmass[int(del_num)]
        return lmass
    else:
        return lmass


def edit_files_list(new_lm=None, mod_lm=None, del_lm=None):
    # новые файлы
    if del_lm is None:
        del_lm = []
    if mod_lm is None:
        mod_lm = []
    if new_lm is None:
        new_lm = []
    choice = 0
    while choice != 3:
        lmass = new_lm
        print_list(lmass, name="new files")
        choice = show_menu()
        new_lm = edit_list(lmass, choice)

    # измененные файлы
    choice = 0
    while choice != 3:
        lmass = mod_lm
        print_list(lmass, name="modify files")
        choice = show_menu()
        mod_lm = edit_list(lmass, choice)

    # удаленные файлы
    choice = 0
    while choice != 3:
        lmass = del_lm
        print_list(lmass, name="delete files")
        choice = show_menu()
        del_lm = edit_list(lmass, choice)

    return new_lm, mod_lm, del_lm
