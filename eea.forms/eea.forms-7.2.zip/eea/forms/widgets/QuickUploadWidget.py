""" QuickUpload Widget based on collective.quickupload package
"""
from Products.Archetypes.Widget import TypesWidget

class QuickUploadWidget(TypesWidget):
    """ Quick Upload Widget via drag&drop.

    Custom properties:

      mediaupload -- Allowed file extensions e.g.: '*.gif; *.tif; *.jpg',
                     empty for all.
                     Default: '*.txt; *.csv; *.tsv; *.tab'
      typeupload  -- portal_type of the destination instance, empty for
                     auto-detect.
                     Default: 'File'
      autorelate  -- Auto relate object with uploaded files, empty for
                     no relations.
                     Default: 'relatedItems'
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "quick_upload_widget",
        'mediaupload' : '*.txt; *.csv; *.tsv; *.tab',
        'typeupload': 'File',
        'autorelate': 'relatedItems',
        'helper_js': ('++resource++eea.forms.quickupload.js',),
    })
