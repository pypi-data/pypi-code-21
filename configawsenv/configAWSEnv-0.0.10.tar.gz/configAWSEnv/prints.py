
class Prints:
    def print_and_exit(self, error, exit_code):
        # todo: replace with logger?
        print("Error: {}".format(error))
        exit(exit_code)