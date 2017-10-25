import core

def complete(text):
    return [text + str(i) for i in range(len(text))]

def main():
    print(core.prompt_autocomplete('ID', complete))
    print(core.prompt_autocomplete('ID', complete, default='123'))
    print(core.prompt_file('FILE:'))
    print(core.prompt_file('FILE:', default='123'))

if __name__ == '__main__':
    main()
