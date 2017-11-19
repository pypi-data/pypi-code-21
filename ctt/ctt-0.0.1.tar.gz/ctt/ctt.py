from bs4 import BeautifulSoup
import re
import sys
import requests
import unidecode


def _get_html(package_id):

    url = 'http://www.ctt.pt/feapl_2/app/open/objectSearch/objectSearch.jspx'
    data = {"showResults": "true", "objects": package_id}
    r = requests.post(url, data=data)
    return r.text


def _convert_date(d):
    f = d.split(' ')
    months = {
        "Janeiro": '01',
        "Fevereiro": "02",
        "Marco": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }
    day = int(f[1])
    if day < 10:
        day = '0' + str(day)

    month = f[2]
    n = month
    month = unidecode.unidecode(n)

    return f[3] + '/' + months[month] + '/' + str(day)


def _is_date(d):
    if re.search('\d{4}$', d) is not None:
        return True
    else:
        return False


def get_package_status(p_id):

    html = _get_html(p_id)
    soup = BeautifulSoup(html, "html.parser")
    d = []
    package = {}

    for td in soup.find_all('td'):
        t = td.string
        if t is not None:
            t = re.sub(r'^\s+', '', re.sub(r'\s+$', '', td.string))
        d.append(t)

    package["id"] = d.pop(0)
    d.pop(0)
    if d[0] == 'N/A':
        package["status"] = [{"status": "Not Found", "date": None, "reason": None, "place": None, "receiver": None}]
        return package

    s_date = d.pop(0)
    s_time = d.pop(0)
    status = d.pop(0)

    package["status"] = [{"status": status, "date": s_date + ' ' + s_time}]
    d.pop(0)
    d.pop(0)
    while (len(d) > 0):
        s_date = d.pop(0)
        if _is_date(s_date):
            s_time = d.pop(0)
            s_date_time = _convert_date(s_date) + ' ' + s_time
        else:
            s_time = s_date
            s_date = package["status"][0]["date"]
            s_date = re.sub(r'\ \d\d:\d\d$', '', s_date)
            s_date_time = s_date + ' ' + s_time

        status = d.pop(0)
        reason = d.pop(0)
        place = d.pop(0)
        receiver = d.pop(0)

        status_data = {
            "status": status,
            "date": s_date_time,
            "reason": reason,
            "place": place,
            "receiver": receiver
        }
        if package["status"][0]["date"] == status_data["date"]:
            package["status"][0]["reason"] = status_data["reason"]
            package["status"][0]["place"] = status_data["place"]
            package["status"][0]["receiver"] = status_data["receiver"]
            if package["status"][0]["status"] == "":
                package["status"][0]["status"] = status_data["status"]

        else:
            package["status"].append(status_data)

    return package

