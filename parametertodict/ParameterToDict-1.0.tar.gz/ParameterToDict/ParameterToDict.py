class PTD(object):

    def __init___(self):

        self.status = "enabled"

    def converter(self, obj=None):

        if obj is not None:

            if '=' not in obj:

                raise SyntaxError("Argument should be valid parameter")

            dictionary = {}
            count = 0

            if '&' in obj:

                obj = obj[0:( len(obj)-1 )] if (obj[len(obj)-1])=='&' else obj
                obj = obj.split('&')

                for element in obj:

                    temp = element.split('=')
                    dictionary[temp[0]]  = temp[1]
                    
                
                return dictionary
                        
            else:
                
                obj = obj.split("=")
                dictionary[obj[0]] = obj[1]
                return dictionary


