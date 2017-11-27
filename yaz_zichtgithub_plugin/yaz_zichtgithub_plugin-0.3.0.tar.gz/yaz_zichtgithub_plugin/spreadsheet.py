from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

from .cache import cache
from .log import logger

__all__ = ["VersionMatrixSheet", "VersionMatrixWorksheet"]


class VersionMatrixSheet:
    def __init__(self, json_key_file: str, sheet_key: str):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scope)
        gc = gspread.authorize(credentials)
        self.sheet = gc.open_by_key(sheet_key)
        self.worksheets = [VersionMatrixWorksheet(worksheet) for worksheet in self.sheet.worksheets()]

    def set_dependencies(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.set_dependencies(*args, **kwargs)

    def set_updating(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.set_updating(*args, **kwargs)

    def unset_updating(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.unset_updating(*args, **kwargs)


class VersionMatrixWorksheet:
    def __init__(self, worksheet):
        self.worksheet = worksheet

    @cache(key=lambda self, *args, **kwargs: (self.worksheet.id, args, kwargs))
    def get_row(self, row, min_col=2):
        return [cell for cell in self.worksheet.range(row, 1, row, self.worksheet.col_count) if cell.col >= min_col]

    @cache(key=lambda self, *args, **kwargs: (self.worksheet.id, args, kwargs))
    def get_column(self, col, min_row=2):
        return [cell for cell in self.worksheet.range(1, col, self.worksheet.row_count, col) if cell.row >= min_row]

    def find_or_create_column_header(self, value, updated_cells):
        cells = self.get_row(1)

        # find existing
        for cell in cells:
            if cell.value == value:
                return cell

        # find available
        for cell in cells:
            if cell.value == "any":
                cell.value = value
                updated_cells.append(cell)
                return cell

        return None

    def find_or_create_row_header(self, value, updated_cells):
        cells = self.get_column(1)

        # find existing
        for cell in cells:
            if cell.value == value:
                return cell

        # find available
        for cell in cells:
            if cell.value == "any":
                cell.value = value
                updated_cells.append(cell)
                return cell

        return None

    def set_dependencies(self, repo, dependencies):
        updated_cells = []

        column_header = self.find_or_create_column_header(repo.name, updated_cells)
        if column_header is None:
            logger.debug("Worksheet #%s: skipping %s because there is no column available", self.worksheet.id, repo.name)
            return
        logger.info("Worksheet #%s: updating %s in column #%s", self.worksheet.id, repo.name, column_header.col)

        version_column = {cell.row: cell for cell in self.get_column(column_header.col)}
        checked_rows = set()

        # check rows that have a dependency
        for dependency, version in dependencies.items():
            row_header = self.find_or_create_row_header(dependency, updated_cells)
            if row_header is None:
                logger.debug("Worksheet #%s: skipping %s because there is no row available", self.worksheet.id, dependency)
                continue

            checked_rows.add(row_header.row)

            if row_header.row in version_column:
                cell = version_column[row_header.row]
            else:
                cell = self.worksheet.cell(row_header.row, column_header.col)
                version_column[row_header.row] = cell

            if cell.value != version:
                logger.info("Worksheet #%s: update dependency %s from \"%s\" to \"%s\"", self.worksheet.id, dependency, cell.value, version)
                cell.value = version
                updated_cells.append(cell)

        # clear rows that do not have a dependency
        for cell in version_column.values():
            if cell.row not in checked_rows:
                if cell.value != "":
                    cell.value = ""
                    updated_cells.append(cell)

        if updated_cells:
            logger.info("Worksheet #%s: persisting %s cells", self.worksheet.id, len(updated_cells))
            self.worksheet.update_cells(updated_cells)

    def set_updating(self, message: str = "UPDATING"):
        cell = self.worksheet.cell(1, 1)
        cell.value = message.format(now=datetime.now())
        self.worksheet.update_cells([cell])

    def unset_updating(self, message: str = "{now}"):
        cell = self.worksheet.cell(1, 1)
        cell.value = message.format(now=datetime.now())
        self.worksheet.update_cells([cell])
