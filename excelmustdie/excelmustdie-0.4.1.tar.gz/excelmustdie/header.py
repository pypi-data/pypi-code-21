import pandas as pd
from matplotlib import pyplot as plt

def named(df, name):
     named.register.append((name, df))
     return df
     
named.register = []

def save_named(name):
    for name_, obj in named.register:
        if name == name_:
            obj.to_csv(name + '.csv')
            print('Saved ' + name + ':')
            print(obj.head())
            
def get_named(name):
    for _name, obj in register:
    	if name == _name:
    		return obj
            
            
def plot_named(name, x, ys, *args, **kwargs):
    for name_, obj in named.register:
        if name == name_:
            cols = obj.columns
            
            for y in ys:
                plt.plot(getattr(obj, x).values.reshape(-1, 1), getattr(obj, y).values.reshape(-1, 1), *args, **kwargs)
                
            plt.xlabel(x)
            plt.ylabel(', '.join(ys))
            plt.savefig('images/' + name)

            return
            
            
def show_image(name):
    plt.imshow(plt.imread('images/' + name + '.png'))
    plt.box(on=False)
    plt.show()
    
def make_title(author=None, date=None, title=None):
    text = ''
    if author is not None:
        text += '\\author{' + author + '}\n'

    if date is not None:
        if date == 'today':
            text += '\\date{\\today}\n'
        else:
            text += '\\date{' + date + '}\n'
            
    if title is not None:
        text += '\\title{' + title + '}\n'
    
    with open('TITLE_TEXT.txt', 'w') as O:
        O.write(text)
