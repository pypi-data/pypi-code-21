def select_option(select_element, option_text):
    """

    :param select_element: Selenium Select object
    :param option_text: The required option visible text, string
    :return: Nothing, the option is selected
    """
    for option in select_element.find_elements_by_tag_name('option'):
        if option.text == option_text:
            option.click()
            return