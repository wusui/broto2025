# Copyright (C) 2025 Warren Usui, MIT License
"""
Find extras stats that can be collected from information listed in other
stat lines
"""

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
