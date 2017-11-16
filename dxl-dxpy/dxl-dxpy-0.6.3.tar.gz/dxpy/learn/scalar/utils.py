def create_global_scalars():
    from . import global_global_step
    from . import global_keep_prob
    global_global_step.create()
    global_keep_prob.create()
