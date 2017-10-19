import sanitize
"Prints the unique 3 best values of a list of data from a bunch of files"
def coach2 (files):
        try:
                for every_file in files:
                    with open (every_file) as file_athlet:
                        data = file_athlet.readline()
                        athlet_data=data.strip().split(',')
                        (athlet_name, athlet_dob) = athlet_data.pop(0), athlet_data.pop(0)
                        data_time=sorted(set([float(sanitize.sanitize(t)) for t in athlet_data]))
                    print ('From file '+every_file+': ')
                    print (athlet_name+"'s fastest times are: "+ str(data_time[0:3]))         
        except IOError as err:
                print ('Fehler1:' +str(err))
        except ValueError as verr:
                print ('Fehler2: ' +str(verr))


