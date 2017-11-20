#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

if __name__ == '__main__':
    fp = open("/Users/mafei/UITest/agent/macaca/reports/index.html")
    soup = BeautifulSoup(fp, 'html.parser')
    print(soup.findAll("li", class_="suite-summary-item failed")[0].string != '0')
