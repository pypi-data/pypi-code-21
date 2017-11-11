# coding: utf-8
from __future__ import print_function
import math
import requests
import jmespath


#def _calc_ab(alpha_a, beta_a, alpha_b, beta_b):
#    '''
#    probability that B beats A
#
#    Code from https://gist.github.com/arnov/60de0b1ad62d329bc222
#    See http://www.evanmiller.org/bayesian-ab-testing.html
#    αA is one plus the number of successes for A
#    βA is one plus the number of failures for A
#    αB is one plus the number of successes for B
#    βB is one plus the number of failures for B
#    '''
#    total = 0.0
#    for i in range(alpha_b-1):
#        num = math.lgamma(alpha_a+i) + math.lgamma(beta_a+beta_b) + math.lgamma(1+i+beta_b) + math.lgamma(alpha_a+beta_a)
#        den = math.log(beta_b+i) + math.lgamma(alpha_a+i+beta_a+beta_b) + math.lgamma(1+i) + math.lgamma(beta_b) + math.lgamma(alpha_a) + math.lgamma(beta_a)
#
#        total += math.exp(num - den)
#    return total


def beta(a, b):
    '''
    Code from https://malishoaib.wordpress.com/2014/04/15/the-beautiful-beta-functions-in-raw-python/
    uses gamma function or inbuilt math.gamma() to compute values of beta function
    '''
    beta = math.gamma(a) * math.gamma(b) / math.gamma(a + b)
    return beta


def _calc_ba(alpha_a, beta_a, alpha_b, beta_b):
    '''
    probability that B beats A

    Code from https://gist.github.com/arnov/60de0b1ad62d329bc222
    See http://www.evanmiller.org/bayesian-ab-testing.html
    αA is one plus the number of successes for A
    βA is one plus the number of failures for A
    αB is one plus the number of successes for B
    βB is one plus the number of failures for B
    '''
    total = 0.0
    for i in range(alpha_b - 1):
        #a1 = lbeta(alpha_a + i, beta_b + beta_a)
        a1 = math.lgamma(alpha_a + i) + math.lgamma(beta_b + beta_a) - math.lgamma(alpha_a + i + beta_b + beta_a)
        a2 = math.log(beta_b + i)
        print(a2)
        #a3 = lbeta(1 + i, beta_b)
        a3 = math.lgamma(1 + i) + math.lgamma(beta_b) - math.lgamma(1 + i + beta_b)
        #a4 = lbeta(alpha_a, beta_a)
        a4 = math.lgamma(alpha_a) + math.lgamma(beta_a) - math.lgamma(alpha_a + beta_a)
        total += math.exp(a1 - a2 - a3 - a4)
        #print(a1 - a2 - a3 -a4)
    return total


def _calc_12_count(alpha_1, beta_1, alpha_2, beta_2):
    total = 0.0
    for k in range(alpha_1 - 1):
        a1 = k * math.log(beta_1)
        a2 = alpha_2 * math.log(beta_2)
        a3 = (k + alpha_2) * math.log(beta_1 + beta_2)
        a4 = math.log(k + alpha_2)
        #a5 = lbeta(k + 1, alpha_2)
        a5 = math.lgamma(k + 1) + math.lgamma(alpha_2) - math.lgamma(k + 1 + alpha_2)
        total += math.exp(a1 + a2 - a3 - a4 - a5)
    return total


#def stats(results):
#    if len(results) != 2:
#        raise
#    a, b = results
#    a['failures'] = a['trials'] - a['successes']
#    b['failures'] = b['trials'] - b['successes']
#    try:
#        prob = _calc_ba(1 + int(a['successes']), 1 + int(a['failures']),
#                        1 + int(b['successes']), 1 + int(b['failures']))
#    except ValueError:
#        prob = _calc_12_count(int(b['successes']), int(b['trials']),
#                              int(a['successes']), int(a['trials']))
#    except:
#        print("(unable to analyze)")
#        return
#    if prob < 0.5:
#        return stats([b, a])
#    print("[{}] > [{}] with {} probability".format(b['label'], a['label'], prob * 100))


def probability(a, others):
    a['failures'] = a['trials'] - a['successes']
    min_prob = 1.0
    for b in others:
        b['failures'] = b['trials'] - b['successes']
        prob = _calc_ba(1 + int(b['successes']), 1 + int(b['failures']),
                        1 + int(a['successes']), 1 + int(a['failures']))
        if prob < 0.5:
            return ''
        min_prob = min(prob, min_prob)
    return ' {0:.2f}% probability to win'.format(min_prob * 100)


def process_goals(goals):
    if goals is None:
        return
    for goal in goals:
        print('%s' % goal['goal'])
        print('---')
        results = goal['results']
        for result in results:
            success = int(result['successes'])
            trials = int(result['trials'])
            #ab_data[result['label']] = (
            #    (1 + int(success)),
            #    (1 + int(trials - success))
            #)
            conversion = 100 * success / trials
            others = [x for x in results if x['label'] != result['label']]
            try:
                winning_chance = probability(result, others)
            except:
                winning_chance = ''
            print('[%s] %0.2f%% (%s, %s)%s' % (result['label'], conversion, success, trials, winning_chance))
        #stats(goal['results'])
        print('---')


def process(data):
    import ipdb; ipdb.set_trace()
    experiments = jmespath.search('[*].[experiment, goals]', data)
    for experiment, goals in experiments:
        if experiment is None:
            continue
        #experiment = el[0]
        #goals = el[1]
        print('experiment: {}'.format(experiment))
        process_goals(goals)


def show(endpoint, api_key, namespace='alephbet'):
    res = requests.get(
        endpoint,
        headers={'x-api-key': api_key},
        params={'namespace': namespace}
    )
    data = res.json()
    process(data)
