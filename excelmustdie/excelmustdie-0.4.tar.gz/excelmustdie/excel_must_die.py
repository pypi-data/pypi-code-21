import os
import json
import re

from excelmustdie import text

def create_report(fname):
    os.chdir('images')
    for name in os.listdir():
        if len(name) > 4 and name[-4:] == '.png':
            name = name[:-4]
            os.system('convert {}.png {}.eps'.format(name, name))
            
    os.chdir('..')


    with open('report.tex', 'w') as O:
        O.write(text.preambule)

    out = ''
    
    try:
        with open('TITLE_TEXT.txt', 'r') as I:
            out = I.read()
    except:
        pass
        
    out += text.head_end
    
    with open(fname + '.ipynb') as I:
        encoder = json.JSONDecoder()
        for cell in encoder.decode(I.read())['cells']:
            if (cell['cell_type'] == 'markdown'):
                for line in cell['source']:
                    line = line.strip()
                    out += '\n'
                    
                    if line.startswith('# '):
                        out += '\section{' + line[2:] + '}'
                    elif line.startswith('## '):
                        out += '\subsection{' + line[2:] + '}'
                    else:
                        out += line
                
            elif cell['cell_type'] == 'code':
                for line in cell['source']:
                    if 'plot_named' in line:
                        pos = line.index('plot_named')
                        
                        endline = line[pos:]
                        
                        firstcav = endline.index("'")
                        lastcav = endline[firstcav+1:].index("'") + firstcav + 1
                        
                        name = endline[firstcav + 1: lastcav]
                        
                        out += '\includegraphics[width=1\linewidth]{' + name + '.eps}'
                    elif 'show_image' in line:
                        imshow_re = re.compile(r'\s*show_image\s*\(["\'](\w+)["\']\)')
                        name = imshow_re.match(line).groups()[0]
                        out += '\includegraphics[width=1\linewidth]{' + name + '.eps}'

    with open('report.tex', 'a') as O:
        O.write(out)
        
        O.write('\n')
        
        O.write(text.term)

    # report created

    os.system('texmaker report.tex')
    
if __name__ == "__main__":
    create_report()
