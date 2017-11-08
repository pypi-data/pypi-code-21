""" Content init module
"""

from Products.validation.config import validation
from eea.sparql.content.validators import SparqlQueryValidator
validation.register(SparqlQueryValidator('isSparqlOverLimit'))
