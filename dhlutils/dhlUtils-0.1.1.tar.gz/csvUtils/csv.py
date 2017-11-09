def load_csv_file_to_dicts(file):
    """
    Loads a csv file to a list of dictionaries
    :param file:
    :return:
    """
    result = []
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for line in reader:
            result.append(line)
    return result


def save_as_csv(entries, file):
    """
    Saves the given entries to the given file
    :param entries:
    :param file:
    :return:
    """
    with open(file, 'w') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, entries[0].keys())
        w.writeheader()
        w.writerows(entries)



def merge_on(entries_1, entries_2, column_1, column_2):
    """
    Add the corrects answers from a csv file. It adds to each line the row i where line[column_1] == answers_csv[i][column_2]
    :param entries_1:
    :param entries_1:
    :param column_1: the column that is looked at for entries_1
    :param column_2: the column that is looked at for entries_2
    :return:
    """
    for l in entries_1:
        value = l[column_1]
        for l2 in entries_2:
            if value == l2[column_2]:
                l.update(l2)
    return entries_1


def split_on_columns(entries, columns, split_name_column, split_name_value):
    """
    Splites on the given columns, uses the split_name_column for a new column, uses split_name_result for the value of the original column
    :param entries:
    :param columns:
    :param split_name_column:
    :param split_name_value:
    :return:
    """
    result = []
    for l in entries:
        for c in columns:
            new_line = {}
            for (k, v) in l.items():
                if k not in columns:
                    new_line[k] = v
                if k == c:
                    new_line[split_name_column] = k
                    new_line[split_name_value] = v
            result.append(new_line)
    return result


def delete_empty_entries(entries, column):
    """
    Deletes a line if the given column is empty
    :param entries:
    :param column:
    :return:
    """
    return [l for l in entries if l[column] != "" and l[column] != " "]


def split_lon_lat(entries, column):
    """
    Splits the lon and lat of the given column
    :param entries:
    :param column:
    :return:
    """
    for l in entries:
        v = l.pop(column)

        l["{}_lat".format(column)] = json.loads(v)['lat']
        l["{}_lon".format(column)] = json.loads(v)['lon']
    return entries



