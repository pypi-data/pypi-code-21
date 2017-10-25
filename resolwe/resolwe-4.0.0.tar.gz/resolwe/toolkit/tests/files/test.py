import psutil
import xlrd

proc = psutil.Process()

print(proc.open_files())

wb = xlrd.open_workbook('file tab.1.xlsx')

print(proc.open_files())

f = open('file tab.1.xlsx')

print(proc.open_files())
