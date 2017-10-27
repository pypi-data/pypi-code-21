import core

def complete(text):
    return [text + str(i) for i in range(len(text))]

def main():
    colors = 'red green blue magenta white cyan yellow black'.split()
    core.prompt_autocomplete('Custom', complete, )
    color = core.prompt_choice('Favourite color', colors)
    core.prompt_file('File', color=color)
    core.prompt_file('Directory', None, True, True, color)
    core.prompt_choice('Favourite color', colors, 'blue', color=color)
    core.prompt_choice('Worst color', colors, show_default=False, default='red')
    
if __name__ == '__main__':
    main()
