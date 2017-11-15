seda_02_languages = {}
extra = {}
for line in open('seda02_base.csv'):
    line = line.strip()
    print line
    code, en_label, fr_label = line.split('|')
    seda_02_languages[en_label] = code
    # for label in en_label.split(';'):
    #     label = label.strip()
    #     assert label not in seda_02_languages
    #     extra[label] = code

output = open('languages.new.csv', 'w')

for line in open('languages-seda1.csv'):
    if not line.startswith(';;'):
        output.write(line)
    else:
        _, _, code3, code2, label = line.split(';')
        label = label.strip()
        if label in seda_02_languages:
            output.write(';;' + ';'.join([code3, seda_02_languages.pop(label), label])+'\n')


output.close()

if seda_02_languages:
    print('remaining languages')
    print '\n'.join(sorted(seda_02_languages))
