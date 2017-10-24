# Python 2 and 3 compatibility
from __future__ import print_function
from builtins import range

import os
import sys
import re

import pickle
import json

import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord


np.seterr(all="raise")
MWA_LOCATION = EarthLocation(lat=-26.756528*u.deg, lon=116.670810*u.deg)

# These regular expressions grab ionospheric data ...
regex_current = re.compile(r"\(iter\s+(\d+):\d+\)\s+{l\s*(\S+),m\s*(\S+)}")
regex_total = re.compile(r"\(iter\s+(\d+):\d+\).*\(TOTAL OFFSET\s+\{l\s*(\S+),m\s*(\S+)\}")
# ... and these grab other useful info.
regex_azza = re.compile(r"az:za=\s*(\S+):\s*(\S+)\):")
regex_cadence = re.compile(r"\s*cadence, min max:\s*\S+\s+(\S+)")
regex_phase = re.compile(r"\s*initial visibility phase centre: ra = (\S+) hrs, dec = (\S+) deg")
regex_obsid = re.compile(r"\s*base file,freq:.*(\d{10})")
regex_rank = re.compile(r"(\S+) \(rank=(\d+\.\d+)\) I=(\d+\.\d+e.\d+),")
regex_iterations = re.compile(r"global args: do_rts: 1, n_iter: (\d+),")
regex_source_info = re.compile(r"#iono# \[(\d+)\] (\S+) (.*)")
regex_iteration = re.compile(r"iter (\d+):00")
regex_sources_copols_stations = re.compile(r"NewGainModel: new set of gain models with (\d+) sources, (\d+) copols, (\d+) stations")


def unwrap_source_ra(sources):
    ra, source_names = [], []
    for s in sources:
        ra.append(sources[s]["ra"])
        source_names.append(s)

    def unwrap(x):
        if x > 270:
            return x - 360
        else:
            return x
    vunwrap = np.vectorize(unwrap)

    if max(ra) > 350 and min(ra) < 10:
        ra = vunwrap(ra).tolist()
        for i, s in enumerate(source_names):
            sources[s]["ra"] = ra[i]


# def azza2radec(azza_array, obs_time):
def azza2radec(az, za, obs_time):
    # az, za = azza_array
    altaz = SkyCoord(az=az, alt=(90-np.array(za)), unit=(u.deg, u.deg), frame="altaz",
                     obstime=obs_time, location=MWA_LOCATION)
    ra = altaz.icrs.fk5.ra.deg
    dec = altaz.icrs.fk5.dec.deg
    # return ra, dec
    return ra.tolist(), dec.tolist()


def lm2radec(ra, dec, l_shifts, m_shifts, metadata):
    """
    From the (RA,Dec) coordinates and the ionospheric shifts in (l,m),
    calculate the apparent source position in (RA,Dec).
    """

    # Convert any NaN values to 0 so calculations can continue.
    # We'll convert them back to NaN later.
    nan_indices = np.isnan(l_shifts)
    l_shifts[nan_indices] = 0
    m_shifts[nan_indices] = 0

    ra = np.deg2rad(ra)
    dec = np.deg2rad(dec)
    phase_centre = metadata["primary_beam_pointing_centre"]
    ra_ref = np.deg2rad(phase_centre[0])
    dec_ref = np.deg2rad(phase_centre[1])
    ra_offset = ra - ra_ref

    # Coordinate transformations: pg. 388 of Synthesis Imaging in Radio Astronomy II.
    # Determine (l,m) from (RA,Dec).
    l = np.cos(dec)*np.sin(ra_offset)
    l += np.deg2rad(l_shifts)
    m = np.sin(dec)*np.cos(dec_ref) - np.cos(dec)*np.sin(dec_ref)*np.cos(ra_offset)
    m += np.deg2rad(m_shifts)

    # Determine new (RA,Dec) coordinates from the shifted (l,m)
    # It appears that 1-l**2-m**2 is not always > 0: cap it.
    rabbit = 1-l**2-m**2
    rabbit[rabbit < 0] = 0
    ra_shifted = np.arctan(l/(np.sqrt(rabbit)*np.cos(dec_ref) - m*np.sin(dec_ref))) + ra_ref
    ra_shifted = (np.rad2deg(ra_shifted) + 180) % 360 - 180
    # The argument to arcsin is not always [-1, 1]: cap that too.
    hare = m*np.cos(dec_ref) + np.sqrt(rabbit)*np.sin(dec_ref)
    hare[hare < -1] = -1
    hare[hare > 1] = 1
    dec_shifted = np.arcsin(hare)
    dec_shifted = np.rad2deg(dec_shifted)

    ra = np.rad2deg(ra)
    dec = np.rad2deg(dec)
    ra_shifts = (ra_shifted - ra)*np.cos(np.deg2rad(dec))
    dec_shifts = dec_shifted - dec

    # Put the NaN values back in.
    l_shifts[nan_indices] = np.nan
    m_shifts[nan_indices] = np.nan
    ra_shifts[nan_indices] = np.nan
    dec_shifts[nan_indices] = np.nan
    return ra_shifts.tolist(), dec_shifts.tolist()


def radec2lm(ra, dec, ra_centre, dec_centre):
    # Coordinate transformations: pg. 388 of Synthesis Imaging in Radio Astronomy II.
    delta_a = np.deg2rad(ra - ra_centre)
    d = np.deg2rad(dec)
    d0 = np.deg2rad(dec_centre)

    l = np.cos(d) * np.sin(delta_a)
    m = np.sin(d) * np.cos(d0) - np.cos(d) * np.sin(d0) * np.cos(delta_a)
    return float(l), float(m)


def extract_obsid(log_filename, log_contents):
    # For many RTS runs, the obsid is in the line with "base file,freq:"
    try:
        return int(regex_obsid.search(log_contents).group(1))
    except AttributeError:
        pass

    # Try the filename for a 10 digit number.
    try:
        return int(re.search(r"(\d{10})", log_filename).group(1))
    except AttributeError:
        pass

    # Try the catalogue line.
    # This should be a last resort, as this catalogue may have been
    # generated for another obsid.
    try:
        return int(re.search(r"(\d{10})", log_filename).group(1))
    except AttributeError:
        pass

    print("Cannot find an obsid for %s" % log_filename, file=sys.stderr)
    exit(1)


def scrape_log_info(log):
    info = {}
    if "master.log" in log:
        return None
    with open(log, 'r') as f:
        obsid = None
        for l in f:
            if "NewGainModel" in l:
                try:
                    # For some reason, the "NewGainModel" line can appear twice.
                    # Ignore the second line.
                    source_count
                    continue
                except NameError:
                    matches = regex_sources_copols_stations.search(l)
                    source_count = int(matches.group(1))
                    copols = int(matches.group(2))
                    stations = int(matches.group(3))
                    # If the source count is 1, this is a useless log.
                    if source_count == 1:
                        return None
            elif "global args" in l:
                iterations = int(regex_iterations.search(l).group(1))
            elif "base file,freq:" in l:
                freq = re.search(r',(\S+)$', l).group(1)
                try:
                    obsid = regex_obsid.search(l).group(1)
                # For some reason, the obsid isn't here. Search the filename for a
                # 10 digit number instead.
                except AttributeError:
                    try:
                        obsid = re.search(r'(\d{10})', log).group(1)
                    # If that fails too, then try the catalogue line.
                    except AttributeError:
                        obsid = None
            elif "catalogue:" in l:
                if not obsid:
                    obsid = re.search(r'(\d{10})', l).group(1)

            if obsid:
                info["log"] = log
                info["obsid"] = obsid
                info["source_count"] = source_count
                info["copols"] = copols
                info["stations"] = stations
                info["iterations"] = iterations
                info["file_size"] = os.path.getsize(log)
                info["band_freq"] = freq
                return info


def filter_logs(logs, verbosity=0):
    obsids = {}

    for l in logs:
        log_info = scrape_log_info(l)
        # If the output is not None, we have useful information.
        if log_info:
            obsid = log_info["obsid"]
            if obsid not in obsids:
                obsids[obsid] = {}
                obsids[obsid]["logs"] = [l]
                obsids[obsid]["source_counts"] = [log_info["source_count"]]
                obsids[obsid]["copols"] = [log_info["copols"]]
                obsids[obsid]["stations"] = [log_info["stations"]]
                obsids[obsid]["iterations"] = [log_info["iterations"]]
                obsids[obsid]["file_size"] = [log_info["file_size"]]
                obsids[obsid]["scores"] = [log_info["source_count"]*log_info["copols"]*log_info["stations"]*log_info["iterations"]*os.path.getsize(l)]
            else:
                obsids[obsid]["logs"].append(l)
                obsids[obsid]["source_counts"].append(log_info["source_count"])
                obsids[obsid]["copols"].append(log_info["copols"])
                obsids[obsid]["stations"].append(log_info["stations"])
                obsids[obsid]["iterations"].append(log_info["iterations"])
                obsids[obsid]["file_size"].append(log_info["file_size"])
                obsids[obsid]["scores"].append(log_info["source_count"]*log_info["copols"]*log_info["stations"]*log_info["iterations"]*log_info["file_size"])

    filtered_logs = []
    for o in obsids:
        obsids[o]["best_log"] = [0, ""]
        for i in range(len(obsids[o]["logs"])):
            if obsids[o]["scores"][i] > obsids[o]["best_log"][0]:
                obsids[o]["best_log"] = [obsids[o]["scores"][i], obsids[o]["logs"][i]]
        filtered_logs.append(obsids[o]["best_log"][1])

    if verbosity > 0:
        for o in obsids:
            print("%s:" % o)
            for i in range(len(obsids[o]["logs"])):
                if obsids[o]["logs"][i] == obsids[o]["best_log"][1]:
                    print("\t[%s],\t%i,\t%i,\t%i,\t%i" % (obsids[o]["logs"][i], obsids[o]["source_counts"][i], obsids[o]["iterations"][i], obsids[o]["file_size"][i], obsids[o]["scores"][i]/1e12))
                else:
                    print("\t%s,\t%i,\t%i,\t%i,\t%i" % (obsids[o]["logs"][i], obsids[o]["source_counts"][i], obsids[o]["iterations"][i], obsids[o]["file_size"][i], obsids[o]["scores"][i]/1e12))
        print("")
    return filtered_logs


def rts2dict(log, flagging=True):
    # Dictionaries for various data.
    sources = {}
    ranks = {}
    metadata = {}

    # Master logs have no useful ionospheric data.
    if "_master.log" in log:
        return
    with open(log, 'r') as f:
        contents = f.read()
        if re.search(r"NOT USED", contents) is not None:
            return

        metadata["obsid"] = extract_obsid(log, contents)
        metadata["time"] = float(re.search(r"initial time: (\S+)", contents).group(1))
        metadata["band_freq"] = float(re.search(r"base file,freq:.*,(\S+)", contents).group(1))
        metadata["iterations"] = int(regex_iterations.search(contents).group(1))
        metadata["cadence"] = float(regex_cadence.search(contents).group(1))

        # The proper pointing direction at the start of the obsid is given by the
        # listed LST minus the listed primary beam pointing centre (given as an hour angle).
        lst = re.search(r"initial lst: (\S+) hrs", contents)
        pb_centre = re.search(r"\s*primary beam pointing centre: ha = (\S+) hrs, dec = (\S+) deg",
                              contents)
        # Multiply by 15 to get the RA in degrees.
        ra_centre = (float(lst.group(1)) - float(pb_centre.group(1))) * 15
        metadata["primary_beam_pointing_centre"] = [ra_centre,
                                                    float(pb_centre.group(2))]

        for r in regex_rank.findall(contents):
            ranks[r[0]] = [float(r[1]), float(r[2])]

        regex_results = regex_source_info.findall(contents)
        # If no sources were found, or only 1 source was found, then skip this log.
        if len(regex_results) <= 1:
            print("%s: One or zero sources. Is this a patch log?" % metadata["obsid"], file=sys.stderr)
            return
        elif len(regex_results) < metadata["iterations"]*len(ranks):
            print("%s: Not enough ionospheric data. Incomplete log?" % metadata["obsid"], file=sys.stderr)
            return

        time = Time(metadata["time"], format="jd")
        az, za = [], []
        for r in regex_results:
            # Add this source's (az, za) coordinates for a bulk astropy
            # sky-coordinate conversion later (really slow otherwise!).
                azza_pair = regex_azza.search(r[2])
                az.append(float(azza_pair.group(1)))
                za.append(float(azza_pair.group(2)))

        ra_c, dec_c = azza2radec(az, za, time)
        # Loop through all ionosphere results, adding them to a dictionary.
        for i, r in enumerate(regex_results):
            # Each source will not be unique; if we haven't seen this source
            # before, add it.
            source = r[1]
            if source not in sources:
                source_number = r[0]
                azza_pair = regex_azza.search(r[2])
                azza_array = [float(azza_pair.group(1)), float(azza_pair.group(2))]
                ra_pos, dec_pos = ra_c[i], dec_c[i]
                l, m = radec2lm(ra_pos, dec_pos, *metadata["primary_beam_pointing_centre"])

                sources[source] = {"source_number": int(source_number),
                                   "azza": azza_array,
                                   "l": l,
                                   "m": m,
                                   "l_shifts": np.zeros(metadata["iterations"]),
                                   "m_shifts": np.zeros(metadata["iterations"]),
                                   "ra": ra_pos,
                                   "dec": dec_pos,
                                   "rank": ranks[source][0],
                                   "flux_density": ranks[source][1]}

        # Now add the ionospheric information in for each source.
        for i, r in enumerate(regex_results):
            source = r[1]
            iteration = int(regex_iteration.search(r[2]).group(1))

            # Capture the offset due to the ionosphere on this line.
            # Note that if "offset too big!!" is on the line, no
            # ionospheric information is present - pretend there's an
            # NaN instead.
            if "offset too big!!" in r[2] or "fit looks bad!!" in r[2]:
                l_shift, m_shift = np.nan, np.nan
            else:
                # If for some reason you want to ionosphere shift since
                # the last iteration, this line captures that.
                # current = regex_current.search(l)

                current = regex_total.search(r[2])
                l_shift, m_shift = float(current.group(2)), float(current.group(3))

            # Don't forget to convert to degrees.
            sources[source]["l_shifts"][iteration] = l_shift/3600
            sources[source]["m_shifts"][iteration] = m_shift/3600

    # Unwrap the right ascensions of the sources if necessary.
    unwrap_source_ra(sources)

    # We now have a partially populated sources dictionary.
    # Delete incomplete ones, and fill in the rest of the info otherwise.
    to_be_deleted = []
    for s in sources:
        # Some sources have no data. Delete them here.
        if len(sources[s]["l_shifts"]) < 4 \
           or np.sum(np.isfinite(sources[s]["l_shifts"])) < metadata["iterations"]*3/4:
            to_be_deleted.append(s)
            continue

        # Scale the ionospheric shifts to match 200 MHz.
        sources[s]["l_shifts"] *= (metadata["band_freq"]**2)/(200**2)
        sources[s]["m_shifts"] *= (metadata["band_freq"]**2)/(200**2)

        # Convert the (l,m) shifts to (RA,Dec) shifts.
        sources[s]["ra_shifts"], \
            sources[s]["dec_shifts"] = lm2radec(sources[s]["ra"],
                                                sources[s]["dec"],
                                                sources[s]["l_shifts"],
                                                sources[s]["m_shifts"],
                                                metadata)
        sources[s]["l_shifts"] = sources[s]["l_shifts"].tolist()
        sources[s]["m_shifts"] = sources[s]["m_shifts"].tolist()

    for s in to_be_deleted:
        del sources[s]

    i, c = metadata["iterations"], metadata["cadence"]
    metadata["timestamps"] = (np.arange(0, c*i, c).astype(int) + metadata["obsid"]).tolist()

    # Bundle the useful bits into a new dictionary.
    product = {}
    product["sources"] = sources
    product["metadata"] = metadata
    return product


def rts2pickle(log, flagging=True):
    # Run the RTS log through the sausage machine.
    data = rts2dict(log, flagging=flagging)
    # If the output was nothing, simply return so no pickle is written.
    if not data:
        return

    filename = "%s.pickle" % data["metadata"]["obsid"]
    with open(filename, 'w') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def rts2json(log, flagging=True):
    # Run the RTS log through the sausage machine.
    data = rts2dict(log, flagging=flagging)
    # If the output was nothing, simply return so no json is written.
    if not data:
        return

    filename = "%s.json" % data["metadata"]["obsid"]
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, separators=(',', ": "))


def rts2yaml(log, flagging=True):
    # YAML is not a standard installed module, so handle importing it only if necessary.
    try:
        import yaml
        from yaml import CDumper as Dumper
    except ImportError:
        try:
            from yaml import Dumper
            print("LibYAML not available - using pure Python implementation (slower).\n", file=sys.stderr)
        except ImportError:
            print("PyYAML not installed - YAML functionality unavailable.\n", file=sys.stderr)

    # Run the RTS log through the sausage machine.
    data = rts2dict(log, flagging=flagging)
    # If the output was nothing, simply return so no yaml is written.
    if not data:
        return

    filename = "%s.yaml" % data["metadata"]["obsid"]
    with open(filename, 'w') as f:
        yaml.dump(data, stream=f, Dumper=Dumper)
