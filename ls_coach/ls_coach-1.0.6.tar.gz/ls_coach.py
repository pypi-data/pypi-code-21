import sanitize

def coach (files,n):
        try:
                if n > 0:
                    with open (files[n-1]) as file_athlet:
                        data = file_athlet.readline()
                        athlet_time=data.strip().split(',')
                        data_clean=sorted([float(sanitize.sanitize(t)) for t in athlet_time])
                        unique_data=[]
                        for e_time in data_clean:
                                if e_time not in unique_data:
                                        unique_data.append(e_time)
                    print (files[n-1]+': ')
                    print (unique_data[0:3])
                    n=n-1
                    coach (files,n)          
        except IOError as err:
                print ('Fehler:' +str(err))
        except ValueError as verr:
                print ('Fehler: ' +str(verr))


