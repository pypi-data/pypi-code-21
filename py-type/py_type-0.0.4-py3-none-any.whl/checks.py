from py_type.output import output

def message(exp, got):
    ### move this into output class
    return 'expected: ' + str(exp) + ', got: ' + str(got)

def check_set(exp, got):
    if set(exp) != set(got):
        output.error_func(message(exp, got))

def check_list(exp, got):
    bs = map(lambda e, g: e==g, exp, got)
    if not all(bs):
        output.error_func(message(exp, got))




