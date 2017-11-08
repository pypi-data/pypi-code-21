
'''
Script to plot summary snowpit from data example of the standard snowpit format
Simon Filhol, December 2016

'''

from snowpyt import pit_class as pc

filename = '/home/tintino/Desktop/Evelein_pit_bug/03052017_snowpit1.xlsx'  #[insert path to file]

pit1 = pc.Snowpit()
pit1.filename = filename
pit1.import_xlsx()
pit1.plot(metadata=True)
pit1.plot(plots_order=['density', 'temperature', 'stratigraphy','crystal size', 'sample value'])

pit1.plot(plots_order=['density', 'sample names','sample values'])



