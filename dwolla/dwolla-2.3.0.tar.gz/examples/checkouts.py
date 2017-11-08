'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the checkouts endpoints.
'''

from dwolla import checkouts

# Step 1: Create checkout session with items from
# http://docs.dwolla.com/#checkouts

test = checkouts.create({
    'orderItems': {
        frozenset({
            'name': 'Prime Rib Sandwich',
            'description': 'A somewhat tasty non-vegetarian sandwich',
            'quantity': '1',
            'price': '15.00'
        })
    },
    'destinationId': '812-740-4294',
    'total': 15.00,
    'notes': 'blahhh',
    'metadata': frozenset({
        'key1': 'something',
        'key2': 'another thing'
    })})

# Step 2: Verify the recently created checkout

checkouts.get(test['CheckoutId'])

# Step 3: Complete the checkout

checkouts.complete('Order ID here')

# Step 4: Verify gateway signature

checkouts.verify('YOUR SIGNATURE HERE', 'YOUR CHECKOUT ID HERE', 4.50)