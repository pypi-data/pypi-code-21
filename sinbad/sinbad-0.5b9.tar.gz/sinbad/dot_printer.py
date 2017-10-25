
from threading import Thread, Event

class Dot_Printer(Thread):
    enabled = True     # globally controls all dot printer objects
    
    max_delay = 2      # seconds
    delay_incr = .25   # seconds
    
    def __init__(self, first_msg, first_msg_delay=max_delay):
        super().__init__(daemon=True)
        self.__stop_it = Event()
        self.__first_msg = first_msg
        self.__first_msg_delay = first_msg_delay
        self.__first_msg_printed = False 
        self.__delay = .5
        
        #signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    def stop(self):
        self.__stop_it.set()
        if self.__first_msg_printed:
            print("Done", flush=True)
    
    def run(self):
        if not Dot_Printer.enabled: return 
        
        self.__stop_it.wait(self.__first_msg_delay)
        if self.__stop_it.is_set(): return
        
        print(self.__first_msg, flush=True)
        self.__first_msg_printed = True
        
        while not self.__stop_it.is_set():
            print(".", sep='', end='', flush=True)
            self.__stop_it.wait(self.__delay)
            if self.__delay < Dot_Printer.max_delay:
                self.__delay = self.__delay + Dot_Printer.delay_incr

