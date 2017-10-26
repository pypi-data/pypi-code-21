"""Miscellanea of miscellanea"""


__all__ = ["random_name"]


import random


_forenames = ["Solomon", "John", "Loretta", "Stephen", "Harry", "Nancy", "Tracy", "Maggie", "Lafanda", "Napoleon", "Joe",
        "Ana", "Olivia", "Lucia", "Julien", "June", "Ada", "Blaise", "Platypus", "R2D2", "Obi-Wan",
        "Yoda", "Lancelot", "Shaun", "C3PO", "Luke", "George", "Martin", "Elvira", "Galileo", "Elizabeth",
        "Genie", "Mark", "Karl", "Henry-David", "Ludmilla", "Darth", "Bayden", "Plamen", "Margareth", "Javier",
        "Pouria", "Klen", "Lydiane", "Charlotte", "Edna", "Ricardo", "Francis", "Jemma", "Valon", "Imran", "Sian",
        "Hayat", "Taghreed", "Orla", "Michael", "Lourdes", "Weiyi", "Thomas", "Willian", "Miguel", "Rui",
        "Abdullah", "Angus", "Malcolm", "Donald", "Mickey", "Polona", "Rashmi", "Xiaowei", "Sasha", "Luciano",
        "Avinash", "Anthony", "Karen", "Matthew", "Tatiana", "Mariana", "Antonio", "Hamilton", "Pauderney",
        "BB-8"]
_surnames = ["Northupp", "Kanobi", "de Morgan", "de Vries", "van Halen", "McFly", "Wallace", "McLeod", "Skywalker", "Smith",
       "Silva", "da Silva", "Sexy", "Coupat", "Coupable", "Byron", "Lovelace", "Pascal", "Kareninski", "Dynamite",
       "Souza", "Ha", "Balboa", "Durden", "V.", "Li", "Manco", "Kelly", "Torquato", "Sampaio", "Bittencourt", "Parisi",
       "Oliveira", "Crap", "Copppercup", "Motherfucker", "Firehead", "Martin", "Papanicolau", "Galilei", "Stuart",
       "Bitch", "King", "Cleese", "Thoreau", "Twain", "Marx", "Yankovicz", "Vader", "Prado", "Teixeira", "Oliveira",
       "Nogueira", "Pereira", "Sant'anna", "Kerns", "Patel", "Ahmadzai", "Riding", "Llabjani", "Maus",
       "Liger", "Byrne", "Wood", "Angelov", "Andreu", "Sadeghi", "Gajjar", "Kara", "Wolstenholme", "Alghaith",
       "Young", "Scott", "Luz", "Copic", "Pucihar", "Zhou", "Dutta", "Baruah", "Singh", "Sauro", "do Nascimento",
       "Lee", "Trevisan", "Travisani", "Pereira", "Nandwani", "Moura", "Senna"]
_prefixes = ["Dr.", "Prof.", "Sir", "Ven."]
_suffixes = ["The 3rd", "Jr.", "Sobrinho", "Neto", "VIII", "XVI", "I", "II", "III", "IV"]
_PROB_PREF = 0.1
_PROB_SUFF = 0.1


def random_name(num_surnames=2):
    """
    Returns a random person name

    Arguments:
      num_surnames -- number of surnames
    """
    a = []

    # Prefix
    if random.random() < _PROB_PREF:
        a.append(_prefixes[random.randint(0, len(_prefixes) - 1)])

    # Forename
    a.append(_forenames[random.randint(0, len(_forenames) - 1)])

    # Surnames
    for i in range(num_surnames):
        a.append(_surnames[random.randint(0, len(_surnames) - 1)])

    # Suffix
    if random.random() < _PROB_SUFF:
        a.append(_suffixes[random.randint(0, len(_suffixes) - 1)])

    return " ".join(a)




# # todo cleanup
# # This is just for debugging
# # http://stackoverflow.com/questions/2023608/check-what-files-are-open-in-python
# import __builtin__
# openfiles = set()
# oldfile = __builtin__.file
# class newfile(oldfile):
#     def __init__(self, *args):
#         self.x = args[0]
#         print "### OPENING %s ###" % str(self.x)
#         oldfile.__init__(self, *args)
#         openfiles.add(self)
#
#     def close(self):
#         print "### CLOSING %s ###" % str(self.x)
#         oldfile.close(self)
#         openfiles.remove(self)
# oldopen = __builtin__.open
# def newopen(*args):
#     return newfile(*args)
# __builtin__.file = newfile
# __builtin__.open = newopen
#
# def printOpenFiles():
#     print "### %d OPEN FILES: [%s]" % (len(openfiles), ", ".join(f.x for f in openfiles))
# __all__.append("printOpenFiles")


# # Logger for internal use
# _logger = logging.getLogger(__name__)
# _logger.addHandler(logging.NullHandler())


