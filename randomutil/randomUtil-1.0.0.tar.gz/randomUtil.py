import random
def GenerateRandomList(size, lower, upper):
    result = []
    for i in range(size):
        result.append(random.randint(lower,upper))
    return result
                      
