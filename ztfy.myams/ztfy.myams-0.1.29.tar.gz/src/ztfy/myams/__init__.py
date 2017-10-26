### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
from fanstatic import Library, Resource

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages


from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ztfy.myams')


library = Library('ztfy.myams', 'resources')

bootstrap_css = Resource(library, 'css/ext/bootstrap-3.3.2.css',
                         minified='css/ext/bootstrap-3.3.2.min.css')
bootstrap_modal_css = Resource(library, 'css/ext/bootstrap-modal.css',
                               minified='css/ext/bootstrap-modal.min.css',
                               depends=[bootstrap_css, ])

awesomefonts_css = Resource(library, 'css/ext/font-awesome-4.5.0.css',
                            minified='css/ext/font-awesome-4.5.0.min.css',
                            depends=[bootstrap_css, ])

myams_css = Resource(library, 'css/myams.css',
                     minified='css/myams.min.css',
                     depends=[bootstrap_modal_css, awesomefonts_css])

jquery = Resource(library, 'js/ext/jquery-2.1.3.js',
                  minified='js/ext/jquery-2.1.3.min.js',
                  bottom=True)

jquery_ui = Resource(library, 'js/ext/jquery-ui-1.11.2.min.js',
                     depends=[jquery, ],
                     bottom=True)

jquery_dataTables = Resource(library, 'js/ext/jquery-dataTables-1.9.4.js',
                             minified='js/ext/jquery-dataTables-1.9.4.min.js',
                             depends=[jquery, ],
                             bottom=True)

jquery_dataTables_tableTools = Resource(library, 'js/ext/jquery-dataTables-tableTools.js',
                                        minified='js/ext/jquery-dataTables-tableTools.min.js',
                                        depends=[jquery_dataTables, ],
                                        bottom=True)

bootstrap = Resource(library, 'js/ext/bootstrap-3.3.2.js',
                     minified='js/ext/bootstrap-3.3.2.min.js',
                     depends=[jquery, jquery_ui, bootstrap_css, bootstrap_modal_css],
                     bottom=True)

myams = Resource(library, 'js/myams.js',
                 minified='js/myams.min.js',
                 depends=[bootstrap, myams_css],
                 bottom=True)
