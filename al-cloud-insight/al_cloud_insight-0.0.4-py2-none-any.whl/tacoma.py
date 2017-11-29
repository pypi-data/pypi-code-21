import png
from gzip import GzipFile
from StringIO import StringIO

class Tacoma(object):
    def __init__(self, parent):
        self.ci = parent.ci.tacoma(parent.version)
        self.account_id = parent.account_id

    def export_saved_view_report(self, site_id, saved_view_id, format_='csv', account_id=None):
        """Returns saved view report for given :account_id and :saved_view_id. Csv reports are compressed with gzip, whilst pdf reports are not compressed.

        https://console.cloudinsight.alertlogic.com/api/tacoma/#api-Saved_Views-ExportSavedViewReport

        /tacoma/v1/:account_id/sites/:site_id/saved_views/:saved_view_id/export"""
        if not account_id:
            account_id = self.account_id
        r = self.ci(account_id).sites(site_id).saved_views(saved_view_id).export.GET(params={'format': format_})
        if format_ is 'csv':
            return GzipFile(fileobj=StringIO(r.content)).read()
        else:
            return r.content

    def get_saved_view(self, site_id, saved_view_id, account_id=None):
        """Get saved view data for given :account_id and :saved_view_id

        https://console.cloudinsight.alertlogic.com/api/tacoma/#api-Saved_Views-GetSavedView

        """
        if not account_id:
            account_id = self.account_id
        r = self.ci(account_id).sites(site_id).saved_views(saved_view_id).GET()
        return r.json()

    def export_view_report(self, site_id, workbook_id, view_id, format_='csv', account_id=None):
        """Returns view report for given :account_id, :workbook_id and :view_id. Csv reports are compressed with gzip, whilst pdf reports are not compressed.

        https://console.cloudinsight.alertlogic.com/api/tacoma/#api-Views-ExportViewReport

        /tacoma/v1/:account_id/sites/:site_id/workbooks/:workbook_id/views/:view_id/export"""
        if not account_id:
            account_id = self.account_id
        r = self.ci(account_id).sites(site_id).workbooks(workbook_id).views(view_id).export.GET(params={'format': format_})
        if format_ is 'csv':
            resp = None
            try:
                resp = GzipFile(fileobj=StringIO(r.content)).read()
            except IOError as error:
                raise Exception('Non-Gzip File found', r.content) 
            else:
                return resp
        else:
            return r.content

    def get_view(self, site_id, workbook_id, view_id, account_id=None):
        """Get view data for given :account_id, :workbook_id and :view_id

        https://console.cloudinsight.alertlogic.com/api/tacoma/#api-Views-GetView

        /tacoma/v1/:account_id/sites/:site_id/workbooks/:workbook_id/views/:view_id"""
        if not account_id:
            account_id = self.account_id
        r = self.ci(account_id).sites(site_id).workbooks(workbook_id).views(view_id).GET()
        return r.json()

    def get_workbook_preview_image(self, site_id, workbook_id, account_id=None):
        """Get preview image (binary PNG) for given :account_id, :site_id and :workbook_id

        https://console.cloudinsight.alertlogic.com/api/tacoma/#api-Workbooks-GetWorkbookPreviewImage

        /tacoma/v1/:account_id/sites/:site_id/workbooks/:workbook_id/preview"""
        if not account_id:
            account_id = self.account_id
        r = self.ci(account_id).sites(site_id).workbooks(workbook_id).preview.GET()
        return png.Reader(file=StringIO(r.content))

    def get_workbooks(self, account_id=None):
        """Get workbooks for given :account_id

        https://console.cloudinsight.alertlogic.com/api/tacoma/#api-Workbooks-GetWorkbooks

        /tacoma/v1/:account_id/workbooks"""
        if not account_id:
            account_id = self.account_id
        r = self.ci(account_id).workbooks.GET()
        return r.json()
