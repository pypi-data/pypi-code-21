from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from form_to_excel.text_mod import TextMod

class PDF:
    def __init__(self, path_to_file):
        self.path = path_to_file

    def to_txt(self):
        rm = PDFResourceManager()
        io = StringIO()
        lp = LAParams()
        tc = TextConverter(rm, io, codec='utf-8', laparams=lp)
        fp = open(self.path, 'rb')
        interpreter = PDFPageInterpreter(rm, tc)
        all_pages = set()
        for page in PDFPage.get_pages(fp, all_pages, maxpages=0, password="",caching=True, check_extractable=True):
            interpreter.process_page(page)

        text = io.getvalue().split('\n')
        question_labels = self.clean_pdf(text)

        fp.close()
        tc.close()
        io.close()
        return question_labels

    def clean_pdf(self, question_labels):
        all_questions = []
        for question in question_labels:
                TextMod.add_question_text(question, all_questions)
        return all_questions
