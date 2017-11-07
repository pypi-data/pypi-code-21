import re

class TextMod:
  def add_question_text(text, questions_list):
    questions = re.split(r'_[\s\t]', text)
    for question in questions:
        text = TextMod.remove_unwanted_characters(question)
        if text:
            questions_list.append(text)
        else:
            continue

  def remove_unwanted_characters(text):
    text_for_question = text.lstrip().strip('_')
    return text_for_question
