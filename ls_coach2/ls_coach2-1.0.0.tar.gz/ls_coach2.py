import sanitize
"Prints the unique 3 best values of a list of data from a bunch of files"
def coach2 (files):
        try:
                for every_file in files:
                    with open (every_file) as file_athlet:
                        data = file_athlet.readline()
                        athlet_time=data.strip().split(',')
                        data_clean=sorted(set([float(sanitize.sanitize(t)) for t in athlet_time]))
                    print (every_file+': ')
                    print (data_clean[0:3])         
        except IOError as err:
                print ('Fehler:' +str(err))
        except ValueError as verr:
                print ('Fehler: ' +str(verr))


