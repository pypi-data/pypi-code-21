""" Custom quick upload controller
"""
from zope.component import getMultiAdapter
from collective.quickupload.browser.quick_upload import (
    QuickUploadView,
    XHR_UPLOAD_JS,
    FLASH_UPLOAD_JS
)


class QuickUploadWidget(QuickUploadView):
    """ Quick Upload View used by QuickUpload Widget
    """
    _mediaupload = ''
    _typeupload = ''

    def script_content(self):
        """ Custom JS
        """
        quickinit = getMultiAdapter((self.context, self.request),
                                    name=u'quick_upload_init')
        quickinit.uploader_id = self.uploader_id
        settings = quickinit.upload_settings()

        # Override global settings
        settings['ul_fill_titles'] = 'false'
        settings['ul_fill_descriptions'] = 'false'
        settings['ul_auto_upload'] = 'true'

        if self._mediaupload:
            ul_content_types_infos = quickinit.ul_content_types_infos(
                self._mediaupload)
            settings['ul_file_extensions'] = ul_content_types_infos[0]
            settings['ul_file_extensions_list'] = str(ul_content_types_infos[1])
            settings['ul_file_description'] = ul_content_types_infos[2]

        xhr_js = XHR_UPLOAD_JS
        if self._typeupload:
            settings['typeupload'] = self._typeupload
            if 'params:' not in xhr_js:
                xhr_js = xhr_js.replace(
                    "autoUpload: auto,",
                    "autoUpload: auto, params: {typeupload: '%(typeupload)s'},"
                )

        if quickinit.qup_prefs.use_flashupload:
            return FLASH_UPLOAD_JS % settings
        return xhr_js % settings

    def __call__(self, **kwargs):
        form = getattr(self.request, 'form', {})
        form.update(kwargs)
        self._mediaupload = form.get('mediaupload', '')
        self._typeupload = form.get('typeupload', '')
        return super(QuickUploadWidget, self).__call__()
