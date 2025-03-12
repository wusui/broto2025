# Copyright (C) 2025 Warren Usui, MIT License
"""
Extract the extra data for one game

TO DO: handle glossary data
To DO: extract extras data in parentheses
"""
import re
from deeper_stats import grand_slams

def extra_convert(peeps, raw_data):
    """
    Handle the 'extra' fields in raw_data
    """
    def proc_extra(lpeeps, extra_stats):
        def handle_stat(estat):
            def hs_inner(entry):
                parts = entry.split()
                count = 1
                if parts[-1].isnumeric():
                    count = int(parts[-1])
                    parts = parts[:-1]
                pname = ' '.join(parts).strip(' ')
                if pname:
                    if not pname[0].isnumeric():
                        prec = list(filter(lambda a: a['name'].endswith(pname),
                                    lpeeps))
                        if len(prec) > 1:
                            print(pname + ' has duplicates')
                        if len(prec) == 1:
                            prec[0][estat[0][0]] = count
            brk = ','
            if ';' in estat[1]:
                brk = ';'
            slist = list(map(lambda a: a.strip(), estat[1].split(brk)))
            list(map(hs_inner, slist))
        clean_stats = list(map(lambda a: re.sub(r'\([^)]*\)', '', a[1]),
                        extra_stats))
        extra_stats = list(zip(extra_stats, clean_stats))
        grand_slams(lpeeps, extra_stats)
        list(map(handle_stat, extra_stats))
    def ec_team(team):
        def ec_team1(borp):
            proc_extra(peeps[team[0]][borp], raw_data[team[1]][borp]['extra'])
        list(map(ec_team1, list(range(2))))
    list(map(ec_team, enumerate(raw_data['score'])))
