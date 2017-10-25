import core

def complete(text):
    return [text + str(i) for i in range(len(text))]

def main():
    print(core.prompt_autocomplete('Custom', complete))
    print(core.prompt_file('File'))
    print(core.prompt_file('Directory', None, True, True))
    print(core.prompt_choice('Favourite color', 'red green blue purple orange pink purple black brown'.split()))
    print(core.prompt_choice('Favourite color', 'red green blue orange pink purple black brown purple'.split(), 'orange'))

if __name__ == '__main__':
    main()
