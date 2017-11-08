import json
from excel_form_builder.question import *
from colorama import *

class ExcelToJson():
"""Convert Excel files to JSON objects."""
    def __init__(self, worksheet, form_name):
        super(ExcelToJson, self).__init__()
        self.worksheet = worksheet
        self.name = form_name

    def find_sheet_values(self):
        sheet_values = []
        for row in self.worksheet.rows:
            row_values = []
            self.list_row_values(row, row_values, sheet_values)
        self.sheet_values = sheet_values

    def list_row_values(self, row, row_values, all_row_values):
        for cell in row:
            if cell.value != None:
                row_values.append(cell.value)
        all_row_values.append(row_values)

    def find_question_indentation(self):
        sheet_indents = []
        for row in self.worksheet.rows:
                indent_count = 0
                self.find_row_indentation(sheet_indents, row, indent_count)
        sheet_indents = list(enumerate(sheet_indents, start=1))
        self.sheet_indents = sheet_indents

    def find_row_indentation(self, all_indents, row, indent_count):
        for cell in row:
            if cell.value == None:
                indent_count+=1
            else:
                break
        all_indents.append(indent_count)

    def merge_indents_with_data(self):
        row_data = [(self.sheet_indents[i][1],self.sheet_values[i],self.sheet_indents[i][0]) for i in range(len(self.sheet_values))]
        self.row_data = row_data

    def remove_blank_rows(self):
        questions_without_blanks = [x for x in self.row_data if len(x[1]) != 0]
        self.form_data = questions_without_blanks

    def create_questions(self):
        valid_question_types = {'sub','grp','clc','dec','int','pwd','loc','img','sk','dt','dtm','tm','txt','txtm','s1','sm','bc','sig','tel','em','sk','yn'}
        questions = []
        for x in self.form_data:
            type = x[1][0]
            if type not in valid_question_types:
                raise ValueError(Fore.RED +"Row {} - Invalid question type provided".format(x[2]))
            else:
                try:
                    questions.append(eval(type)(x[0],x[1][0],x[1][1],x[1][2:],x[2]))
                except IndexError:
                    raise Exception(Fore.RED +"Row {} - Question name not provided".format(x[2]))
        self.form_questions = questions

    def create_identifiers(self):
        for question in self.form_questions:
            identifier = question.name[:]
            before_id = []
            for character in identifier:
            	if character.isalpha() == False and character.isdigit() == False:
            	    before_id.append(character.replace(character,"_"))
            	else:
            	    before_id.append(character)
            if before_id[0].isdigit():
            	before_id.insert(0,"_")
            question.properties["identifier"] = "".join(before_id)

    def addhints(self):
            # All hints are added to questions and removed from select options.
        for question in self.form_questions:
            cell_count = 0
            for cell in question.extra_cells:
                if str(cell).startswith(":"):
                    description = question.extra_cells.pop(cell_count)
                    new_hint = description.replace(":","")
                    question.properties["hint"] = new_hint
                cell_count += 1
        return

    def check_for_select_questions(self):
        # Select options are added for s1 and sm questions.
        for question in self.form_questions:
            if len(question.extra_cells) > 0:
                self.add_select_options(question)
        return

    def add_select_options(self, question):
        if question.type == 's1' or question.type == 'sm':
            options = []
            for option in question.extra_cells:
                options.append({ "text": "{}".format(option)})
            question.properties["options"] = options
        else:
            raise Exception(Fore.RED +"Row {} - Select options passed to a non-select question".format(question.row_number))

    def add_question_groups(self):
        question_list = [[]]
        last_indent = 0
        for child in self.form_questions:
            if child.properties["type"] == "group":
                self.add_question_attributes(child, last_indent, question_list)
                question_list.append([])
            else:
                self.add_question_attributes(child, last_indent, question_list)
            last_indent = child.indent
        if len(question_list) > 1:
            self.pop_last_to_group(question_list)
        self.form_questions = question_list

    def add_question_attributes(self, child, last_indent, question_list):
        if child.indent < last_indent:
            for x in range(last_indent - child.indent):
                question_list[-1][-1]['children'] = question_list.pop()
        elif child.indent >= len(question_list):
            raise Exception(Fore.RED +"Row {} - Excessive indentation".format(child.row_number))
        question_list[-1].append(child.properties)

    def pop_last_to_group(self, question_list):
        for item in range(len(question_list) - 1):
            question_list[-1][-1]['children'] = question_list.pop()
        return question_list


    def addbase(self):
        base = { "type": "root", "children": self.form_questions[0], "title": self.name, "description": "Created by DM" }
        self.json = base


    def create_json(self):
        with open("{}.json".format(self.name), "w") as json_file:
            json.dump(self.json, json_file)
        print(Fore.GREEN + "Form created!")

    def create_form(self):
        self.find_sheet_values()
        self.find_question_indentation()
        self.merge_indents_with_data()
        self.remove_blank_rows()
        self.create_questions()
        self.create_identifiers()
        self.addhints()
        self.check_for_select_questions()
        self.add_question_groups()
        self.addbase()
        self.create_json()
        return
