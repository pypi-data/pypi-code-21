
import datetime, os, sys

class Logger:
    
    def __init__(self, log_dir):
        self.log_dir = log_dir
        
        self.log_list = []
        self.create_log_file()

    def log(self, message, error=False, neverprint=False):
        if error:
            message = 'ERROR: ' + message
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        if self.debug and not neverprint:
            sys.stdout.write(message + '\n')
            sys.stdout.flush() #forces output now
        try:
            with open(self.log_path, 'a') as f:
                [f.write(item) for item in self.log_list] #log anything saved in memory that couldn't be written before
                f.write(message)
                f.write('\n')
            self.log_list = []
        except PermissionError: #if someone happened to write to the file at the same time
            self.log_list.append(message) #save it to log later
            self.log_list.append('\n')

    def create_log_file(self):
        name = 'log_' + str(datetime.datetime.now().replace(microsecond=0)).replace(':','.') + '.txt'
        if not os.path.exists(self.log_dir): os.makedirs(self.log_dir)
        self.log_path = os.path.join(self.log_dir, name)

        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as f:
                f.write('\n')


        