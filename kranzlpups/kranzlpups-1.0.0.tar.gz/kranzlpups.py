""" Dieses Modul ist mein erstes Modul der Listen Schachtler
zur Ausgabe von verschachtelten Listen """


def print_lvl(liste):
	""" Es wird eine Liste durchlaufen und je Datenelement geprueft ob jenes 
	wiederum eine Liste ist. Wenn ja, rufe erneut die Funktion auf. Wenn nein,
	printe das Element """
	for element in liste:
		if isinstance(element, list):
			print_lvl(element)
		else:
			print(element)
