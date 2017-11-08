import CodeReview.TextDistance as TD

# print(TD.levenshtein_distance("foo bar", "fo oooooooo bar"))
# print(TD.levenshtein_distance("foo bar", "fo oo bar"))
# print(TD.levenshtein_distance("foo bar", "fo ar"))
# print(TD.levenshtein_distance("foo bar", "zoo laaaaa"))
print(TD.levenshtein_distance("saturday", "sunday"))
print(TD.levenshtein_distance("sunday", "saturday"))
print(TD.levenshtein_distance("kitten", "sitting"))
