import os
try:
    input = input
except NameError:
    pass

altdir = input('Type the path of the folder where to save the results (leave empty to remove the choice): ')

if altdir:
    ad = open('altdir.txt', 'w')
    ad.write(altdir + '\n')
    ad.close()
else:
    try:
        os.remove('altdir.txt')
    except IOError:
        pass
