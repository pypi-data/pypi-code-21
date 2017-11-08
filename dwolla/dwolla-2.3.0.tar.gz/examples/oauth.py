'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the OAuth endpoints.
'''

from dwolla import oauth, constants

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "XK+XHoxLkx5Fc7sdfgsdfgsdfgdsfdfga5o3EWaxzaQi+/r8yV0s"
constants.client_secret = "8gfuoig5y909hjnohf/L+vfmX0NOkok/SkXWbDtX8HvH7"

# Step 1: Generate an OAuth permissions page URL
# with your application's default set redirect.
#
# http://requestb.in is a service that catches
# redirect responses. Go over to their URL and make
# your own so that you may conveniently catch the
# redirect parameters.


# You can view your responses at:
# http://requestb.in/[some_id]?inspect
#
# If you're feeling dangerous, feel free to simply use
# http://google.com and manually parse the parameters
# out yourself. The choice remains yours.

print(oauth.genauthurl("http://requestb.in/122rdhc1"))

# Step 2: The redirect should provide you with a `code`
# parameter. You will now exchange this code for an access
# and refresh token pair.

access_set = oauth.get("Z/KHDIyWO/LboIGn3wGGs1+sRWg=", "http://requestb.in/122rdhc1")
print(access_set)

# Step 2.5: If you wish, you can set the library's global
# access token parameter by doing the following...

constants.access_token = access_set['access_token']

# Step 3: Exchange your expiring refresh token for another
# access/refresh token pair.x

access_set = oauth.refresh(access_set['refresh_token'])
print(access_set)

# Step 4: Retrieve the catalog of endpoints that
# are available to the OAuth token which you just
# retrieved.

print(oauth.catalog())
