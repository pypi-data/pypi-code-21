
import sanitize

class Athlete:
    def __init__(self, a_name, a_pob=None, a_dob=None, a_times=[]):
        self.name = a_name
        self.dob = a_dob
        self.pob = a_pob
        self.times = a_times
        print(self.name+ " ,born in " + str(self.pob) + ",'s fastest times are: " + str(self.top3()))
    def top3(self):
        return(sorted(set([sanitize.sanitize(t) for t in self.times]))[0:3])

    def add_time(self,time_value):
        self.times.append(time_value)

    def add_times(self,time_list):
        self.times.extend(time_list)

    def add_pob(self,pob):
        self.pob = append.pob
                
def get_coach_data(filename):
    try:
        with open(filename) as f:
            data = f.readline()
        templ = data.strip().split(',')
        return(Athlete(templ.pop(0), templ.pop(0), templ))
    except IOError as ioerr:
        print('File error: ' + str(ioerr))
        return(None)
