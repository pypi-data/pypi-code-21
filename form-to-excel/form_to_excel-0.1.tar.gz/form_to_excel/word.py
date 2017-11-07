from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from form_to_excel.text_mod import TextMod

class Word():
  def __init__(self, path_to_file):
    self.path = path_to_file

  def iter_table_items(self, parent):
    if isinstance(parent, _Document):
      parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
      parent_elm = parent._tc
    else:
      raise ValueError("Unknown object within document, please inspect.")
    for child in parent_elm.iterchildren():
      if isinstance(child, CT_Tbl):
        yield Table(child, parent)
      elif isinstance(child, CT_P):
        yield Paragraph(child, parent)

  def to_txt(self):
    document = Document(self.path)
    fullText = []
    for block in self.iter_table_items(document):
      if isinstance(block, Paragraph):
        TextMod.add_question_text(block.text, fullText)
      elif isinstance(block, Table):
        self.table_add(block, fullText)
    return fullText

  def table_add(self, table, all_questions):
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                TextMod.add_question_text(paragraph.text, all_questions)
