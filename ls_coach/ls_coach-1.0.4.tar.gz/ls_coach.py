import sanitize
def coach (files,n):
        try:
                if n > 0:
                    with open (files[n-1]) as james:
                        data = james.readline()
                        james_line=data.sanitize().strip().split(',')
                    print (files[n-1]+': ')
                    print(sorted(james_line))
                    n=n-1
                    coach (files,n)          
        except IOError as err:
                print ('Fehler:' +str(err))
        except ValueError as verr:
                print ('Fehler: ' +str(verr))

