import sanitize
"Prints the unique 3 best values of a list of data from a bunch of files"
def coach2 (files):
        try:
                for every_file in files:
                    with open (every_file) as file_athlet:
                        data = file_athlet.readline()
                athlet_data=data.strip().split(',')
                athlet = {}
                athlet['Name'] = athlet_data.pop(0),
                athlet['DoB'] = athlet_data.pop(0),
                athlet['Time'] = sorted(set([sanitize.sanitize(t) for t in athlet_data]))
                print ('From file '+every_file+': ')
                print (str(athlet['Name'])+"'s fastest times are: "+  str(athlet['Time'][0:3]))
        except IOError as err:
                print ('Fehler1:' +str(err))
        except ValueError as verr:
                print ('Fehler2: ' +str(verr))


