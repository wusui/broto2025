# Copyright (C) 2025 Warren Usui, MIT License
"""
Reformat scraped data into player records
"""
from extra_convert import extra_convert

def proc_stats(stats):
    """
    Process player stats (mostly the 'table' section of the raw data)
    """
    def pit_data():
        def out_calc(iparts):
            return int(iparts[0]) * 3 + int(iparts[1])
        outs = out_calc(stats[0].split('.'))
        pairs = list(zip(['H', 'R', 'ER', 'BB', 'K', 'HR'],
                         list(map(int, stats[1:7]))))
        out_dict = dict(pairs)
        out_dict['outs'] = outs
        return out_dict
    def bat_data():
        pairs = list(zip(['AB', 'RH', 'HH', 'RBI', 'HRH', 'BBH', 'KH'],
                         list(map(int, stats[0:7]))))
        return dict(pairs)
    if '.' in stats[0]:
        return pit_data()
    return bat_data()

def convert_data(raw_data):
    """
    Convert the data scraped into lists of dicts where the elements of each
    dict are all specific fields in a player's record.
    """
    def set_pos(ppos):
        if not ppos:
            return 'P'
        return ppos
    def cd_teams(team):
        def cd_pos(pindx):
            def cd_player(entry):
                phead = {'id': entry[0][0][0], 'name': entry[0][0][1],
                        'pos': set_pos(entry[0][1][0]), 'team': team,
                        'app': 1, 'game': raw_data['one_line']}
                phead.update(proc_stats(entry[1]))
                return phead
            return list(map(cd_player, raw_data[team][pindx]['table']))
        return list(map(cd_pos, range(2)))
    def ostart(tm_inf):
        subs = list(map(lambda a: a.split('|')[-2],
                        raw_data[tm_inf[1]][0]['subs']))
        return list(filter(lambda a: a['name'] not in subs,
                           peeps[tm_inf[0]][0]))
    def p_strt_set(sbatter):
        def psr_inner(strt):
            strt['start'] = 1
        list(map(psr_inner, sbatter))
    def set_bhswl():
        def get_pits(vhpits):
            return list(filter(lambda a: a['name'] in apits, vhpits))
        def set_pstat(pers):
            def sp_inn(indv):
                def pupdate(pentry):
                    def pupdate2(value):
                        ptrn = {'W': 'Win', 'L': 'Loss', 'S': 'Save',
                                'H': 'Hold', 'B': 'Blown_Save'}
                        indv[ptrn[value]] = 1
                    list(map(pupdate2, pentry[1]))
                pit_ent = list(filter(lambda a: a[0] == indv['name'],
                                raw_data['pit_data']))
                list(map(pupdate, pit_ent))
            list(map(sp_inn, pers))
        apits = list(map(lambda a: a[0], raw_data['pit_data']))
        vpeeps, hpeeps = list(map(get_pits, [peeps[0][1], peeps[1][1]]))
        set_pstat(vpeeps)
        set_pstat(hpeeps)
    def set_ph_stats(phinfo):
        def sps_inner(action):
            indx = list(filter(lambda a: a[1] == phinfo[0],
                        list(enumerate(raw_data['score']))))[0][0]
            phitter = list(filter(lambda a: a[0][1][1] == action[0],
                        raw_data[phinfo[0]][0]['table']))[0][0][0][1]
            ph_rec = list(filter(lambda a: a['name'].endswith(phitter),
                            peeps[indx][0]))[0]
            act1 = action[0:action.find(' in the ')]
            act2 = act1[act1.rfind(' for '):][5:]
            ph_rep = list(filter(lambda a: a['name'].endswith(act2),
                            peeps[indx][0]))[0]
            ph_rep['ph_for'] = 1
            if action[1:].startswith('-walked') or action[1:].startswith(
                        '-hit by pitch'):
                return
            ph_rec['phab'] = 1
            afront = action[2:].split(' ')[0]
            if afront in ['singled', 'doubled', 'tripled', 'homered']:
                ph_rec['ph_hit'] = 1
            if afront == 'reached' and action.find('single') >= 0:
                ph_rec['ph_hlt'] = 1
        if phinfo[1]:
            list(map(sps_inner, phinfo[1].split('|')))
    if not raw_data:
        return []
    peeps = list(map(cd_teams, list(raw_data['score'].keys())))
    peeps[0][1][0]['start'] = 1
    peeps[1][1][0]['start'] = 1
    if len(peeps[0][1]) == 1:
        peeps[0][1][0]['CG'] = 1
    if len(peeps[1][1]) == 1:
        peeps[1][1][0]['CG'] = 1
    bstrts = list(map(ostart, enumerate(list(raw_data['score'].keys()))))
    list(map(p_strt_set, bstrts))
    set_bhswl()
    phinfo = list(map(lambda a: [a, raw_data[a][0]['glossary']],
                list(raw_data)[0:2]))
    list(map(set_ph_stats, phinfo))
    extra_convert(peeps, raw_data)
    return peeps
