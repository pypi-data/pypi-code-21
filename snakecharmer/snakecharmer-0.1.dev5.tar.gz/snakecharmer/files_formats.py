def paired(wildcards, target_char="@", prefix=".", suffix="fa", with_unpaired=False):
    template = "{}/{}.{}".format(prefix, wildcards.name, suffix)
    cohort = [
        template.replace(target_char, "1"),
        template.replace(target_char, "2")
    ]
    if with_unpaired:
        cohort.append(template.replace(target_char, "U"))
    return cohort
