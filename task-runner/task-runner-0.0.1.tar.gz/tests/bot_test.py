from .context import TaskRunner

current_round = 0
def reset_round():
    global current_round
    current_round = 0

def no_args():
    return True

def with_args(arg):
    return arg

def with_exclusions():
    global current_round
    current_round += 1
    return current_round > 10

def with_exceptions():
    global current_round
    current_round += 1
    if current_round > 10:
        return True
    else:
        raise Exception('Exception raised!')

def test_no_args():
    task_runner = TaskRunner()
    result = task_runner.run_until_complete(target=no_args)
    assert result == True

def test_with_args():
    task_runner = TaskRunner()
    arg = 123
    result = task_runner.run_until_complete(target=with_args, args=(arg,))
    assert result == arg

def test_with_exclusions():
    reset_round()
    task_runner = TaskRunner()
    result = task_runner.run_until_complete(target=with_exclusions, exclude=[False])
    assert result == True

def test_with_exceptions():
    reset_round()
    task_runner = TaskRunner()
    result = task_runner.run_until_complete(target=with_exceptions)
    assert result == True
