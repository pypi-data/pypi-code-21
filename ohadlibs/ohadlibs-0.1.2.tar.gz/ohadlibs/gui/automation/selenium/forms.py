class LoginForm:

    def __init__(self, webdriver, username, password):
        """
        This object should handle arbitrary logins based on username and password fields, with a button as submit method.
        :param webdriver: Selenium webriver object
        :param username: string
        :param password: string
        """
        self.username = username
        self.password = password

    def login(self):
        self.driver.get(paths['cloudshell_host'])
        inputs = self.driver.find_elements_by_tag_name('form')[0].find_elements_by_tag_name('input')[:2]
        inputs[0].send_keys(self.username)
        inputs[1].send_keys(self.password)
        self.driver.find_elements_by_tag_name('button')[0].click()