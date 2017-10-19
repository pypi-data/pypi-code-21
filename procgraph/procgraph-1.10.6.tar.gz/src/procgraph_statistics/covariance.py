from procgraph  import register_model_spec

# XXX: make models directory

register_model_spec("""
--- model covariance
''' Computes the covariance matrix of the input. '''
input x 'Unidimensional numpy array.'
output cov_x 'Square matrix representing sample covariance.'
config wait=10 'Number of sample to have reliable expectation.'

|input name=x| --> x --> |expectation| --> |wait n=$wait| --> Ex

   x, Ex --> |sync| --> |-| --> x_normalized 
   
   x_normalized, x_normalized --> |outer| -->  |expectation| --> covariance 
   
   covariance --> |output name=cov_x|
    
""")

register_model_spec("""
--- model normalize 
''' Removes the mean from a signal. '''
input  x       'Unidimensional numpy array.'
output x_n     'Signal without the mean.'
config wait=10 'Number of sample to have reliable expectation.'

|input name=x| --> x --> |expectation| --> |wait n=$wait| --> Ex

   x, Ex --> |sync| --> |-| --> x_normalized --> |output name=x_n|
    
""")
