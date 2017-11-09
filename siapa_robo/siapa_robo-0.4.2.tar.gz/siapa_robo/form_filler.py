import csv
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (StaleElementReferenceException,
                                        NoSuchElementException,
                                        NoSuchFrameException)
from selenium.webdriver.support.ui import WebDriverWait


def load_csv(csv_file, delimiter=";"):
    with open(csv_file, "r") as f:
        data = list(csv.DictReader(f, delimiter=";"))
    return data


class Field():
    def __init__(self, field_obj):
        self.field = field_obj

    @property
    def name(self):
        name = self.field.get_attribute("name")
        return name

    @property
    def input_type(self):
        INPUT_NAMES = {"text": "text",
                       "select-one": "drop_down",
                       "radio": "radio"}

        field_type = self.field.get_attribute("type")
        return INPUT_NAMES[field_type]

    @property
    def options(self):
        if self.input_type == "drop_down":
            field_options = self.get_field_options()
            return field_options
        else:
            return None

    def get_field_options(self):
        opts = [Option(o) for o in \
                self.field.find_elements_by_tag_name("option")]
        return opts

    def send_keys(self, keys):
        self.field.send_keys(keys)

    def clear(self):
        self.field.clear()

    def submit(self):
        self.field.submit()


class Option():
    def __init__(self, option_obj):
        self.option = option_obj
        self.value = self.option.get_attribute("value")
        self.text = self.option.text

    def __repr__(self):
        return f"Valor: {self.value} | Texto: {self.text}"

    def click(self):
        self.option.click()


class Form():
    def __init__(self, driver):
        self.driver = driver
        self.form = self.get_form_from_source()

    def submit(self, button="Consultar"):
        '''
        Tenta fazer o submit do formulário e realiza um click para checar
        se houve sucesso. Caso não tenha atualizado, tenta clicar nos botões
        Avançar ou Consultar
        '''
        try:
            self.driver.find_element_by_name(button).click()
        except NoSuchElementException:
            if button == "Consultar":
                alt_button = "Avancar"
            else:
                alt_button = "Consultar"

            try:
                self.driver.find_element_by_name(alt_button).click()
            except NoSuchElementException:
                self.form.submit()

    def get_form_from_source(self):
        TIMEOUT = 2
        wait = WebDriverWait(self.driver, TIMEOUT)
        form = wait.until(EC.visibility_of_element_located((By.TAG_NAME,
                                                            "form")))
        return form

    def get_field_options(self, field):
        options_list = []
        for option in field.find_elements_by_tag_name("option"):
            options_list.append(Option(option))

        return options_list

    @property
    def fields(self):
        field_list = {}
        FORM_FIELD_TAGS = ["input", "select"]

        for tag in FORM_FIELD_TAGS:
            try:
                form_fields = self.form.find_elements_by_tag_name(tag)
            except NoSuchElementException:
                pass
            else:
                for field in form_fields:
                    field_type = field.get_attribute("type")
                    FIELD_IS_NOT_HIDDEN = field_type != "hidden"
                    if FIELD_IS_NOT_HIDDEN:
                        f = Field(field)
                        field_list[f.name] = f
        return field_list

    def map(self, csv_file, delimiter=";", callback=None):
        fields_count = len(self.fields)
        csv_data = load_csv(csv_file, delimiter=delimiter)

        # Checa se os dados contem uma coluna para cada campo do formulario
        for i in csv_data:
            if len(i) != fields_count:
                raise ValueError("O formato dos dados não está conforme "
                                 "com o formulário")

        # checa se o nome das colunas esta de acordo com o nome dos
        # campos do formulário
        data_fields = csv_data[0].keys()
        for field in data_fields:
            assert field in [self.fields[i].name for i in self.fields]

        # inicia o preenchimento sequencial com os dados do csv_file
        for i in csv_data:
            for key in i:
                # espera o campo carregar no DOM
                wait = WebDriverWait(self.driver, 2)
                wait.until(EC.visibility_of_element_located((By.NAME, key)))

                field = self.fields[key]
                if field.input_type == "text":
                    field.clear()
                    field.send_keys(i[key])

                if field.input_type == "drop_down":
                    for option in field.options:
                        if i[key] == option.text:
                            option.click()
                            break

            self.submit()

            # executa o callback
            if callback is not None:
                callback()
                self.driver.back()
                # captura novamente os elementos do formulário
                try:
                    self.driver.switch_to_frame("Principal")
                except NoSuchFrameException:
                    pass
                self.form = self.get_form_from_source()
