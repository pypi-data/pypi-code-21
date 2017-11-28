import cpuinfo

def get_cpu_info(to_display=False, detailed=False):
    info = cpuinfo.get_cpu_info()
    if to_display:
        to_display = get_cpu_info_strings(info, detailed)
        for line in to_display:
            print line
    return info

def get_cpu_info_strings(info, detailed):
    to_display = []
    not_relevant = ["flags", "model", "extended_model", "l2_cache_line_size", "family", "l2_cache_associativity",
                    "hz_advertised_raw", "hz_actual_raw", "raw_arch_string", "stepping", "cpuinfo_version",
                    "vendor_id"]

    for key, value in info.iteritems():
        sugar_key = key.replace("_", " ")
        if key not in not_relevant and not detailed:
            to_display.append(sugar_key + ": " + str(value))
        elif detailed:
            to_display.append(sugar_key + ": " + str(value))
    return to_display
