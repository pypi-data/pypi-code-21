from procgraph import register_model_spec

# XXX: make models/ directory

register_model_spec("""
--- model variance 
''' Computes the element-wise variance. '''
input x 'Any numpy array'
output var_x 'Variance of ``x``.'
config wait = 100 "Number of samples to wait before declaring the value valid."

|input name=x| --> x --> |expectation| --> |wait n=$wait| --> Ex

   x, Ex --> |sync| --> |-| --> error 
   
   error -> |square| --> |expectation| --> |output name=var_x|
    
""")

register_model_spec("""
--- model soft_variance 
''' Computes the element-wise "soft" variance (exp. of error abs. value) '''
config wait = 100 "Number of samples to wait before declaring the value valid."
input x 'Any numpy array'
output var_x 'Soft variance of ``x``.'

|input name=x| --> x --> |expectation| --> |wait n=$wait| --> Ex

   x, Ex --> |sync| --> |-| --> error 
   
   error -> |abs| --> |expectation| --> |output name=var_x|
    
""")
