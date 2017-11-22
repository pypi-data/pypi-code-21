from . import Step

try:
    from PyQt5.QtGui import QPageSize, QPageLayout
    from PyQt5.QtCore import QUrl, QCoreApplication, QObject, QFile, QIODevice, QEventLoop, QSizeF, Qt, QMarginsF
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWebEngineWidgets import QWebEngineView

    class QtPDF(Step):

        def __init__(config):
            super().__init__(config)

        def __call__(self, name, content, metadata, fonts):

            filename = '{0}.html'.format(name)
            output = '{0}.pdf'.format(name)

            width = 210
            if 'width' in metadata:
                width = metadata['width']

            height = 297
            if 'height' in metadata:
                height = metadata['height']

            write_file(filename, content)

            self.process_file(filename, width, height, output)

        def process_file(self, filename, width, height, output):

            from pyvirtualdisplay import Display
            xephyr = Display(visible=False, size=(320, 240), backend='xvfb').start()

            web = HTMLPDFProcessor.Render(os.path.join(os.getcwd(), filename))

            page_size = QPageSize(QSizeF(width, height), QPageSize.Millimeter)
            layout = QPageLayout(page_size, QPageLayout.Portrait, QMarginsF())

            def get_callback(url):

                def callback(data):

                    file = QFile(url)
                    file.open(QIODevice.WriteOnly)
                    file.write(data)
                    web.app.quit()

                return callback

            web.page().runJavaScript('''
var section_height = $('section').outerHeight();

real_section_height = section_height - (2 * (section_height * 0.1))

$('.slide').each(function(index)
{
  var slide_height = $(this).outerHeight();

  if(slide_height > real_section_height)
  {
    var ratio = real_section_height / slide_height;
    $(this).css('zoom', ratio);
  }
});
''')
            web.page().printToPdf(get_callback(output), layout)

            web.app.exec_()

        class Render(QWebEngineView):

            def __init__(self, file):

                self.html = None
                self.app = QApplication(sys.argv)
                QWebEngineView.__init__(self)
                self.loadFinished.connect(self._loadFinished)

                self.load(QUrl('file://{0}'.format(file)))

                while self.html is None:
                    self.app.processEvents(QEventLoop.ExcludeUserInputEvents | QEventLoop.ExcludeSocketNotifiers | QEventLoop.WaitForMoreEvents)

            def _callable(self, data):
                self.html = data

            def _loadFinished(self, result):
                self.page().toHtml(self._callable)

except:

    class QtPDF(Step):
        pass
