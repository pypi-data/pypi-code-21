def integrate_odeint(*arguments,**keyword_arguments):
    import scipy.integrate
    
    logger.info('beginning integration')
    result = scipy.integrate.odeint(*arguments,**keyword_arguments)
    logger.info('finished integration')
    return result
