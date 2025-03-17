# Copyright (C) 2025 Warren Usui, MIT License
"""
Extract the extra data for one game

TO DO: handle glossary data
To DO: extract extras data in parentheses
"""
import re
from deeper_stats import grand_slams, hbp_rem, def_extras, hndl_risp, hndl_dptp

def extra_convert(peeps, raw_data):
    """
    Handle the 'extra' fields in raw_data
    """
    def proc_extra(lpeeps, extra_stats):
        def get_tm_indx():
            return list(raw_data['score']).index(lpeeps[0]['team'])
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
                            if estat[0][0] not in prec[0]:
                                prec[0][estat[0][0]] = 0
                            prec[0][estat[0][0]] += count
            def hbp_loc(binc):
                hbp_rem(binc, get_tm_indx(), peeps)
            brk = ','
            if ';' in estat[1]:
                brk = ';'
            slist = list(map(lambda a: a.strip(), estat[1].split(brk)))
            if estat[0][0] == 'HBP':
                list(map(hbp_loc, estat[0][1].split(brk)))
                return
            list(map(hs_inner, slist))
            if estat[0][0] in ['2B', '3B', 'SB', 'CS', 'Picked Off']:
                def_extras(estat, 1 - get_tm_indx(), peeps)
            if estat[0][0] == 'Team RISP':
                hndl_risp(estat, get_tm_indx(), peeps)
            if estat[0][0] in ['DP', 'TP']:
                hndl_dptp(estat, get_tm_indx(), peeps)
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
