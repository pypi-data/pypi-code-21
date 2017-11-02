import sys
import os
import csv

from apiclient import discovery
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class ManageSheet:
    def __init__(self, doc_name, sheet=None):
        self._sheet = sheet

        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        file_list = (drive.ListFile({'q': "title = '{}'".format(doc_name)})
                     .GetList())
        for file1 in file_list[:1]:
            service = discovery.build('sheets', 'v4', http=gauth.http)
            self._spreadsheetId = file1['id']
            self._gvalues = service.spreadsheets().values()

    def get(self, sheet=None):
        return self._gvalues.get(spreadsheetId=self._spreadsheetId,
                                 range=sheet if sheet else self._sheet).execute()

    def update(self, result):
        return self._gvalues.update(spreadsheetId=self._spreadsheetId,
                                    range=result['range'],
                                    valueInputOption='RAW',
                                    body=result).execute()

    def append(self, values):
        return self._gvalues.append(spreadsheetId=self._spreadsheetId,
                                    range=self._sheet,
                                    valueInputOption='RAW',
                                    body={'values': values}).execute()


def generate_spreadsheet(doc_name, sheet):
    gsheet = ManageSheet(doc_name, sheet)
    print('\nGetting [{}]"{}" ...'.format(doc_name, sheet))
    result = gsheet.get()
    return result.get('values', [])


def generate_spreadsheet_csv(doc_name, sheet):
    values = generate_spreadsheet(doc_name, sheet)
    fname = '{} - {}.csv'.format(doc_name, sheet)
    print('Generating {} ...'.format(fname))
    with open(fname, 'w', newline='\n', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        maxcols = max(len(row) for row in values)
        for row in values:
            if len(row) < maxcols:
                row += ([''] * (maxcols - len(row)))
            writer.writerow(row)
    return fname
