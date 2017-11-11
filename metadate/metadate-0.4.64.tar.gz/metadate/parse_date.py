import re
from datetime import datetime

from dateutil.relativedelta import relativedelta as rd

from metadate.classes import (MetaBetween, MetaModifier, MetaOrdinal,
                              MetaPeriod, MetaRange, MetaRelative, MetaUnit)
from metadate.scanner import Scanner
from metadate.utils import Units, BOUNDARIES, erase_level, log, resolve_end_period
from metadate.classes import MetaAnd

import metadate.locales.en as locale_en
import metadate.locales.nl as locale_nl

# TODO: have to make locale lazy still
lang_to_scanner = {
    "en": Scanner(locale_en),
    "nl": Scanner(locale_nl)
}

lang_to_locale = {
    "en": locale_en,
    "nl": locale_nl
}


def get_relevant_parts(matches):
    strike = 0
    bundles = [[]]
    for m in matches:
        if isinstance(m, str):
            strike = 1
        else:
            if strike:
                bundles.append([m])
            else:
                bundles[-1].append(m)
            strike = 0
    return bundles


def between_allowed(x, y, text):
    start = x.span[1]
    end = y.span[0]
    return re.match("^[ -]*(and)?[ -]*$", text[start:end])


def merge_ordinal_unit(matches, text):
    news = []
    t = 0
    last = False
    n = len(matches)
    spans = []
    for i, m in enumerate(matches):
        if i != n - 1 and isinstance(m, MetaOrdinal):
            if last and not between_allowed(last, m, text):
                t = 0
            t += float(m.amount)
            last = m
            spans.append(m.span)
            continue
        elif isinstance(m, MetaUnit):
            m.modifier *= t if t else 1
            m.span = [m.span] + spans
            spans = []
        news.append(m)
    return news


def cleanup_relevant_parts(bundles, locale):
    cleaned_bundles = []
    for bundle in bundles:
        modifier = False
        meta_units = []
        new = []
        for x in bundle:
            if isinstance(x, MetaModifier):  # "this"
                if meta_units:
                    for mu in meta_units:
                        unit = mu.unit.lower() + 's'
                        rd_kwargs = {unit: mu.modifier * locale.MODIFIERS[x.x]}
                        new.append(MetaRelative(level=Units[mu.unit], span=[
                                   x.span, mu.span], **rd_kwargs))
                modifier = x
                meta_units = []
            elif isinstance(x, MetaAnd):
                continue
            elif modifier:
                if isinstance(x, MetaUnit):
                    if x.unit == "quarter":
                        rd_kwargs = {"months": 3 * x.modifier * locale.MODIFIERS[modifier.x],
                                     "day": 1}
                    else:
                        unit = x.unit.lower() + 's'
                        rd_kwargs = {unit: x.modifier * locale.MODIFIERS[modifier.x]}
                    new.append(MetaRelative(level=Units[x.unit], span=[
                               x.span, modifier.span], **rd_kwargs))
                # elif isinstance(x, MetaDate):
                #     # if hasattr(x, "month"):
                #     #     print("relative", x.month, modifier)
                #     # if hasattr(x, "season"):
                #     #     print("relative", x.season, modifier)
                #     new.append(x)
                elif isinstance(x, MetaRelative):

                    if x.rd.weekday is not None:
                        # eg "next" tuesday adds +1 week
                        weeks = locale.MODIFIERS[modifier.x]
                        # "this" also adds +1, "past" should be -1
                        if weeks == 0:
                            weeks = 1
                        x.rd.weeks += weeks
                        modifier = False

                    new.append(x)

            elif isinstance(x, MetaUnit):
                meta_units.append(x)
                modifier = False
            else:
                if not isinstance(x, MetaOrdinal):
                    new.append(x)
                # meta_units = []
                # modifier = False
        cleaned_bundles.append(new)
    cleaned_bundles = [x for x in cleaned_bundles if any([isinstance(y, MetaRelative) for y in x])]
    return cleaned_bundles


def flatten_inner(l):
    span = []
    for s in l:
        if isinstance(s, list):
            span.extend(flatten_span(s))
        else:
            span.append(s)
    return span


def flatten_span(l):
    return sorted(set(flatten_inner(l)))


def get_min_level(cleaned_bundle):
    level = 100
    for x in cleaned_bundle:
        if isinstance(x, (MetaRelative, MetaUnit)):
            level = min(x.level, level)
    return level


def datify(cleaned_bundle, past_boundary, now):
    span = flatten_span([x.span for x in cleaned_bundle])
    level = get_min_level(cleaned_bundle)
    # print(level)
    rdt, erdt = resolve_dt(cleaned_bundle, now)

    if erdt is not None:
        start_date = rdt + resolve_rd(cleaned_bundle)
        end_date = erdt + resolve_rd(cleaned_bundle)
        start_date, _, _ = resolve_end_period(start_date, level, past_boundary, now)
        end_date = erase_level(erdt, level)
    else:
        resolved_rd = resolve_rd(cleaned_bundle)
        try:
            start_date = rdt + resolved_rd
        except TypeError:
            resolved_rd.years = int(resolved_rd.years)
            resolved_rd.months = int(resolved_rd.months)
            start_date = rdt + resolved_rd

        start_date, end_date, _ = resolve_end_period(start_date, level, past_boundary, now)
    return start_date, end_date, level, span


# flexible for running with a default init of locale_en
en_scanner = Scanner(locale_en)


def has_between(bundle):
    return any(isinstance(x, MetaBetween) for x in bundle)


def merge_dt(mdt, dt):
    # mdt is a made-up mutable dt
    # month is precomputed so that day can be init
    month = mdt[1] if mdt[1] > -1 else dt.month
    day = mdt[2] if mdt[2] > -1 else dt.day
    ndt = datetime(year=mdt[0] if mdt[0] > -1 else dt.year,
                   month=month,
                   day=min(day, BOUNDARIES[month]),
                   hour=mdt[3] if mdt[3] > -1 else dt.hour,
                   minute=mdt[4] if mdt[4] > -1 else dt.minute,
                   second=mdt[5] if mdt[5] > -1 else dt.second,
                   microsecond=mdt[6] if mdt[6] > -1 else dt.microsecond)
    return ndt


def resolve_dt(cleaned_bundle, now):
    # the concept of checking whether there is overlap is good, and crash?
    indices = {'year': 0, 'month': 1, 'day': 2, 'hour': 3,
               'minute': 4, 'second': 5, 'microsecond': 6}
    dts = [-1, -1, -1, -1, -1, -1, -1]
    edts = [-1, -1, -1, -1, -1, -1, -1]
    contains_between = has_between(cleaned_bundle)
    # for d in cleaned_bundle:
    #     if isinstance(d, MetaDate):
    #         for x in d.__dict__:
    #             if x not in ['level', 'span', 'now']:
    #                 if dts[indices[x]] != -1:
    #                     if not contains_between:
    #                         raise ValueError("Field already known in dt, should not overwrite?")
    #                 else:
    #                     dts[indices[x]] = getattr(d, x)
    #                 edts[indices[x]] = getattr(d, x)
    dt = merge_dt(dts, now)
    edt = merge_dt(edts, now) if contains_between else None
    return dt, edt


def resolve_rd(cleaned_bundle):
    rds = rd()
    for d in cleaned_bundle:
        if isinstance(d, MetaRelative):
            other = d.rd
            # "on sunday 12th of may" --- adding weekday + day should
            # remove corrective weekday +7 days
            if rds.weekday is not None and other.day is not None:
                rds.days = 0
            if other.weekday is not None and rds.day is not None:
                other.days = 0
            rds += other
    return rds


def handle_meta_range(cleaned_bundle, past_boundary, locale, text):
    now = datetime.now()
    phase = 0
    mrange = None
    relatives = []
    metadates = []
    for x in cleaned_bundle:
        if phase == 0 and isinstance(x, MetaRange):
            phase = 1
            mrange = x
        elif phase == 1 or phase == 2 and isinstance(x, MetaRelative):
            phase = 2
            relatives.append(x)
        elif phase == 2 or phase == 3 and isinstance(x, MetaDate):
            phase = 3
            metadates.append(x)
    if phase < 2:
        return None
    # case 1: MetaRange, MetaRelative, MetaRelative, etc
    # log("relatives", relatives, True)
    # log("metadates", metadates, True)
    if not metadates:
        # in this case, the start_date becomes "now" adjusted for level
        # the end_date is the start_date + relativedeltas following
        level = get_min_level(relatives)
        rds = rd()
        start_date = erase_level(now, 1)
        for x in relatives:
            if x.rd is None:
                continue
            rds += x.rd
        try:
            end_date = start_date + rds
        except TypeError:
            rds.years = int(rds.years)
            rds.months = int(rds.months)
            end_date = start_date + rds
        span = flatten_span([mrange.span, [x.span for x in relatives]])
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        return MetaPeriod(start_date, end_date, level, span, locale.NAME, text)
    else:
        spans = flatten_span([flatten_span(x.span) for x in relatives])
        words = [text[x[0]:x[1]].lower() for x in spans]
        # generic
        dt, _ = resolve_dt(metadates, now)
        dt_level = get_min_level(metadates)
        rd_level = get_min_level(relatives)
        if "first" in words:
            # this is actually the logic for !first! days of, not "next days of"
            # case 2: MetaRange, MetaRelative, MetaRelative, etc, MetaDate, Metadate, etc
            start_date, _, date_changed = resolve_end_period(dt, dt_level, past_boundary, now)
            end_date = erase_level(dt, dt_level) + resolve_rd(relatives)
        elif "last" in words:
            _, end_date, date_changed = resolve_end_period(dt, dt_level, past_boundary, now)
            start_date = erase_level(end_date, dt_level) + resolve_rd(relatives)
        else:
            raise NotImplementedError("What's the case here?")
    if date_changed:
        start_date = start_date + rd(years=1)  # I think also here?
        end_date = end_date + rd(years=1)
    span = flatten_span([mrange.span] + [x.span for x in relatives] +
                        [x.span for x in metadates])
    return MetaPeriod(start_date, end_date, min(rd_level, dt_level), span, locale.NAME, text)


def parse_date(text, future=rd(years=30), past=rd(years=100), lang="en", reference_date=None, multi=False, verbose=False,
               min_level=None, max_level=None, return_early=0):
    now = reference_date or datetime.now()
    past = past or rd()
    future = future or rd()
    locale = lang_to_locale[lang]
    log("\nSentence", text, verbose)
    scanner = lang_to_scanner[lang]
    matches, _ = scanner.scan(text)
    log("matches", matches, verbose=verbose)
    parts = get_relevant_parts(matches)
    log("1", parts, verbose=verbose)
    if return_early == 1:
        return parts
    merged = [merge_ordinal_unit(x, text) for x in parts]
    if return_early == 2:
        return merged
    log("2", merged, verbose=verbose)
    cleaned_parts = cleanup_relevant_parts(merged, locale)
    if return_early == 3:
        return cleaned_parts
    log("3", cleaned_parts, verbose)

    if not cleaned_parts:
        return [] if multi else None

    cleaned_parts = sorted(cleaned_parts, key=len, reverse=True)

    mps = []
    past_boundary = now - past
    future_boundary = now + future
    for cleaned_bundle in cleaned_parts:
        if mps and mps[0] and not multi:
            return mps[0]
        handle_meta_result = handle_meta_range(cleaned_bundle, past_boundary, locale, text)
        if handle_meta_result:
            log("4meta", handle_meta_result, verbose)
            mps.append(handle_meta_result)
            continue

        start_date, end_date, level, span = datify(cleaned_bundle, past_boundary, now)

        mp = MetaPeriod(start_date, end_date, level, span, locale.NAME, text)

        if min_level is not None and mp.level < min_level:
            continue

        if max_level is not None and mp.level > min_level:
            continue

        log("4default", mp, verbose)
        if past_boundary <= mp.start_date <= future_boundary:
            mps.append(mp)

    if not multi:
        if mps:
            return mps[0]
        else:
            return None

    return mps
