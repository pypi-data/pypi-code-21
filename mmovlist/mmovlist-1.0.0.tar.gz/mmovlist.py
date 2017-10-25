"""zhe shi yige mokuai"""
def man_movie(argu):
        """zheshi zhege hanshu de suite"""
        for i in argu:
                if isinstance(i,list):
                        man_movie(i)
                else:
                        print (i)

