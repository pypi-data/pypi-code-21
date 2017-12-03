class AbstractEase(object):

    # For options see: http://easings.net/da and http://www.gizma.com/easing/
    # for explanation see: http://upshots.org/actionscript/jsas-understanding-easing

    @classmethod
    def calculate_next_step(self, current_step, start_value, change_in_value, number_of_steps):
        raise  ("You should have implemented this")

