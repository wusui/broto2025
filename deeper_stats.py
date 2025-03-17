# Copyright (C) 2025 Warren Usui, MIT License
"""
Find extras stats that can be collected from information listed in other
stat lines
"""
from itertools import chain

def grand_slams(lpeeps, extra_stats):
    """
    Find grand slams by scanning for homers with 3 on.
    """
    def rm_cnt(hr_data):
        hr_nm = hr_data[0:hr_data.find('(')].strip()
        if hr_nm[-1].isnumeric():
            hr_nm = hr_nm[0:-1]
        return hr_nm.strip()
    def set_gs(bdata):
        plyr = list(filter(lambda a: a['name'].endswith(bdata[0]), lpeeps))
        if len(plyr) > 1:
            print(f'{bdata[0]} is not unique')
        else:
            plyr[0]['grand slams'] = bdata[1]
    hrs = list(filter(lambda a: a[0][0] == 'HR', extra_stats))
    if not hrs:
        return
    parts = hrs[0][0][1].split(';')
    counts = list(map(lambda a: len(a.split(' 3 on, ')) - 1, parts))
    names = list(map(rm_cnt, parts))
    pinfo = list(filter(lambda a: a[1] > 0, list(zip(names, counts))))
    list(map(set_gs, pinfo))

def hbp_rem(binc, pind, peeps):
    """
    Collect HBP stats for both batters and pitchers
    """
    def evall(tindx, posindx, hbpdata):
        def ieval(plyr):
            numb = 1
            plyr = plyr.strip()
            if plyr[-1].isnumeric():
                numb = int(plyr[-1])
                plyr = plyr[:-1].strip()
            plist = list(filter(lambda a: a['name'].endswith(plyr),
                                            peeps[tindx][posindx]))
            if len(plist) != 1:
                print('HBP Error', plist)
            if len(plist) != 0:
                statn = ['HBP', 'BHBP'][posindx]
                if statn in plist[0]:
                    plist[0][statn] += numb
                else:
                    plist[0][statn] = numb
        list(map(ieval, hbpdata))
    parts = binc[0:-1].split(" (by ")
    bind = 1 - pind
    evall(bind, 0, [parts[0]])
    evall(pind, 1, parts[1].split(","))

def def_extras(estat, tmindx, peeps):
    """
    Handle extra data (usually defensive) for doubles, triples, stolen bases,
    caught stealing, and pickoffs. (HRs allowed already in table)
    """
    def de_inner(pin_paren):
        if estat[0][0] in ['SB', 'CS']:
            def chk_battery(battery):
                def add_lvalue(fpeep):
                    sname = f"def_{estat[0][0]}"
                    if len(fpeep) == 0:
                        print(f"{estat[0][0]} error: player not found")
                        return
                    if len(fpeep) > 1:
                        print(f"{estat[0][0]} error: Multiple entries")
                    if sname not in list(fpeep[0]):
                        fpeep[0][sname] = 1
                    else:
                        fpeep[0][sname] += 1
                ctv = ''
                if '/' not in battery:
                    ptv = battery
                else:
                    ptv, ctv = list(map(lambda a: a.strip(),
                                        battery.split('/')))
                pdata = list(filter(lambda a: a['name'].endswith(ptv),
                            peeps[tmindx][1]))
                add_lvalue(pdata)
                if ctv:
                    cdata = list(filter(lambda a: a['name'].endswith(ctv),
                                peeps[tmindx][0]))
                    add_lvalue(cdata)
            sb_brk = {'SB': ' off ', 'CS': ' by '}[estat[0][0]]
            pin_paren = pin_paren[0:-1].split(',')[1:]
            drun_list = list(map(lambda a: a[a.find(sb_brk) +
                            len(sb_brk):], pin_paren))
            list(map(chk_battery, drun_list))
        if estat[0][0] in ['2B', '3B', 'Picked Off']:
            def stat_inn(indiv):
                count = 1
                if indiv[-1].isnumeric():
                    count = int(indiv[-1])
                    indiv = indiv[0:-1].strip()
                pstat = list(filter(lambda a: a['name'].endswith(indiv),
                                    peeps[tmindx][1]))
                if len(pstat) != 1:
                    if estat[0][0] == 'Picked Off':
                        cpeeps = list(filter(lambda a:
                                    a['name'].endswith(indiv),
                                    peeps[tmindx][0]))
                        if len(cpeeps) == 1 and cpeeps[0]['pos'] == 'C':
                            if 'Def Pick Off' not in cpeeps[0]:
                                cpeeps[0]['Def Pick Off'] = 0
                            cpeeps[0]['Def Pick Off'] += count
                            return
                    print(f'stat {estat[0][0]} has issue involving {indiv}')
                if len(pstat) == 0:
                    return
                if estat[0][0] not in pstat[0]:
                    pstat[0][estat[0][0]] = 0
                pstat[0][estat[0][0]] += count
            def lev2_splt(ptext):
                return list(map(lambda a: a.strip(), ptext.split(',')[1:]))
            defp0 = pin_paren.split(')')[0:-1]
            defp1 = list(map(lambda a: a[a.find('(') + 1:], defp0))
            defp2 = list(map(lev2_splt, defp1))
            defp3 = list(chain.from_iterable(defp2))
            list(map(stat_inn, defp3))
    list(map(de_inner, estat[0][1].split(';')))

def hndl_risp(estat, tmindx, peeps):
    """
    Collect RISP H and AB stats
    """
    def hrisp_inner(stat):
        parts = stat.split()
        pname = ' '.join(parts[0:-1])
        numbs = list(map(int, parts[-1].split('-')))
        pers = list(filter(lambda a: a['name'].endswith(pname),
                           peeps[tmindx][0]))
        if len(pers) == 0:
            print(f"risp error finding {pname}")
            return
        if len(pers) > 1:
            print(f"possible risp error, duplicate {pname}")
        pers[0]['RISP_H'] = numbs[0]
        pers[0]['RISP_AB'] = numbs[1]
    info = estat[0][1][estat[0][1].find('('):][1: -1]
    list(map(hrisp_inner, info.split(',')))

def hndl_dptp(estat, tmindx, peeps):
    """
    Collect stats for defensive DPs and TPs
    """
    def hdptp_inner(stat):
        def dptp_get(person):
            stat_id = estat[0][0]
            pers = list(filter(lambda a: a['name'].endswith(person),
                        peeps[tmindx][0]))
            if len(pers) == 0:
                pers = list(filter(lambda a: a['name'].endswith(person),
                        peeps[tmindx][1]))
                if len(pers) == 0:
                    print(f"{stat_id} error finding {person}")
                    return
            if len(pers) > 1:
                print(f"{stat_id} Possible dup error in {person}")
            label = f"def {stat_id}"
            if label not in pers[0]:
                pers[0][label] = 0
            pers[0][label] += count
        stat = stat.strip()
        count = 1
        if stat[-1].isdigit():
            count = int(stat[-1])
            stat = stat[0:-1].strip()
        list(map(dptp_get, stat.split('-')))
    info = estat[0][1][estat[0][1].find('('):][1: -1]
    list(map(hdptp_inner, info.split(',')))
