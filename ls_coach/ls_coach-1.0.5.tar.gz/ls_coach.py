import sanitize
def coach (files,n):
        try:
                if n > 0:
                    with open (files[n-1]) as file_athlet:
                        data = file_athlet.readline()
                        athlet_time=data.strip().split(',')
                        data_clean=[sanitize.sanitize(each_time) for each_time in athlet_time]
                    print (files[n-1]+': ')

                    print (sorted(data_clean))
                    n=n-1
                    coach (files,n)          
        except IOError as err:
                print ('Fehler:' +str(err))
        except ValueError as verr:
                print ('Fehler: ' +str(verr))



