#!/usr/bin/env python


# test union client
# test models

from random import randint
import union

all_customers = union.Customer.all()
print all_customers


# print '********* TEST NEW'
# # Test New
# cust = union.Customer(name='Test Create %s' % randint(1,100))
# cust.save()
# print cust.id

# print '********* TEST UPDATE'
# # Test Update
# cust = union.Customer.get('cust-1b0ec45988b9')
# cust.name = 'Test Company %s' % randint(1,100)
# cust.save()
# print cust
