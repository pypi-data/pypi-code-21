# -*- coding: utf-8 -*-

#  888888    db    88     88  dP  dP"Yb  88b 88 88""Yb Yb  dP      dP""b8 88     88 888888 88b 88 888888 
#  88__     dPYb   88     88odP  dP   Yb 88Yb88 88__dP  YbdP      dP   `" 88     88 88__   88Yb88   88   
#  88""    dP__Yb  88  .o 88"Yb  Yb   dP 88 Y88 88"Yb    8P       Yb      88  .o 88 88""   88 Y88   88   
#  88     dP""""Yb 88ood8 88  Yb  YbodP  88  Y8 88  Yb  dP         YboodP 88ood8 88 888888 88  Y8   88   

"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""
from falkonryclient.helper import schema as schemas
from falkonryclient.service import falkonry


client = falkonry.FalkonryService
__all__ = [
  'client',
  'schemas'
]
__title__     = 'falkonryclient'
__version__   = '1.0.4'
__author__    = 'Falkonry Inc'
__copyright__ = 'Copyright 2016 Falkonry Inc'
__license__   = """
The MIT License (MIT)

Copyright (c) 2016 Falkonry Inc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
