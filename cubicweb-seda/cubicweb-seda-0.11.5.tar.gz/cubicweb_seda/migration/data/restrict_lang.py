seda_2_languages = set((line.strip() for line in open('languages.csv.temp')))

output = open('languages-seda2.csv', 'w')

for line in open('languages.csv'):
    if not line.startswith(';;'):
        output.write(line)
    else:
        _, _, code3, code2, label = line.split(';')
        if code2 in seda_2_languages:
            output.write(line)

output.close()
