from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from prettytable import PrettyTable


class Methods:

    _page_source = None

    def __init__(self, driver, bar):
        # web driver
        self._driver = driver
        self._bar = bar

    # get gpa
    def _prepare_driver_for_gpa(self):

        # switch to menu and enter gpa page
        self._bar.update(70)
        self._driver.switch_to.frame('menu')
        self._driver.find_element_by_xpath('/html/body/table/tbody/tr[8]/td/table/tbody/tr[2]/td/a').click()
        self._driver.switch_to.default_content()
        self._driver.switch_to.frame('body')

        # commit button
        self._commit_button = self._driver.find_element_by_xpath('//*[@id="taniReferListForm"]/table/tfoot/tr/td/input[1]')
        self._bar.update(80)

    def gpa(self):
        self._prepare_driver_for_gpa()

        # commit
        self._bar.update(90)
        self._commit_button.click()
        self._page_source = self._driver.page_source

        # get gpa data
        self._bar.update(100)
        self._bar.finish()
        self._get_data_for_gpa()

    def gpa_by(self, year, term):
        self._prepare_driver_for_gpa()

        # switch to year and term selection
        self._bar.update(90)
        self._driver.find_element_by_xpath('//*[@id="spanType2"]').click()

        # input year and select term
        self._driver.find_element_by_id('nendo').send_keys(str(year))
        Select(self._driver.find_element_by_name('gakkiKbnCd')).select_by_value(str(term))

        # commit
        self._bar.update(100)
        self._bar.finish()
        self._commit_button.click()
        self._page_source = self._driver.page_source
        self._get_data_for_gpa()

    def _get_data_for_gpa(self):
        count = 0
        soup = BeautifulSoup(self._page_source, 'lxml')

        # get user info table
        user_info = soup.find_all('tbody')[1]
        heads = user_info.find_all('th')
        values = user_info.find_all('td')

        # make table and print
        user_info_table = PrettyTable([heads[0].text.strip(), values[0].text.strip()])
        for index in range(1, len(heads)):
            user_info_table.add_row([heads[index].text.strip(), values[index].text.strip()])
        print(user_info_table)

        # get gpa details head
        heads = []
        for head in soup.find('thead').find('tr'):
            if head.string.strip() == '':
                continue
            heads.append(head.string.strip())

        # get gpa details value
        values = []
        for row in soup.find_all('tbody')[2].find_all('tr'):
            values.append([])
            for value in row.find_all('td'):
                values[count].append(value.string.strip())
            count += 1

        # make table and print
        count = 1
        gpa_details_table = PrettyTable([heads[0], heads[4], heads[5], heads[6], heads[7], heads[8], heads[9]])
        for row in values:
            gpa_details_table.add_row([count, row[4], row[5], row[6], row[7], row[8], row[9]])
            count += 1
        print(gpa_details_table)

    # get lecture
    def _prepare_for_lecture(self):
        # switch to menu and enter gpa page
        self._bar.update(70)
        self._driver.switch_to.frame('menu')
        self._driver.find_element_by_xpath('/html/body/table/tbody/tr[6]/td/table/tbody/tr[2]/td/a/span').click()
        self._driver.switch_to.default_content()
        self._driver.switch_to.frame('body')

        # get page source and parse to soup
        self._bar.update(80)
        self._page_source = self._driver.page_source

    def lecture(self):
        self._bar.update(90)
        self._prepare_for_lecture()

        # switch to first term
        self._bar.update(100)
        self._bar.finish()
        self._get_data_for_lecture()

    def _get_data_for_lecture(self):
        soup = BeautifulSoup(self._page_source, 'lxml')
        week = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日']
        order = ['1限', '2限', '3限', '4限', '5限', '6限', '7限']

        # get all lecture
        lectures = []
        for lecture in soup.find_all('table', class_='rishu-koma-inner'):
            class_id = lecture.find_all('td')[0].contents[2].strip()
            if class_id == '':
                lectures.append('/')
            else:
                lectures.append(class_id)

        # print lecture list
        table = PrettyTable()
        table.add_column('時間割', order)
        for index in range(5):
            tmp = []
            for count in range(7):
                tmp.append(lectures[index + 6 * count])
            table.add_column(week[index], tmp)
        print(table)
