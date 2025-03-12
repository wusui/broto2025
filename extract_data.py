# Copyright (C) 2025 Warren Usui, MIT License
"""
Scrape relevant data into a dictionary
"""
from itertools import chain

def lget_text(pinfo):
    """
    Get text without failing on empty input
    """
    if not pinfo:
        return []
    return pinfo.text

def table_fix(binfo):
    """
    Extract data from the table in this soup fragment
    """
    def b_ext_inner(pinfo):
        if not pinfo:
            return []
        return (pinfo['href'].split('/')[-1], pinfo.text)
    def get_numbs(stat):
        return list(map(lambda a: a.text, stat.find_all('td')))
    tinfo = binfo.find_all('table')
    peeps = tinfo[0].find_all('tr')
    stats = list(map(get_numbs, tinfo[1].find_all('tr')))
    ninfo1 = list(map(lambda a: b_ext_inner(a.find('a')), peeps))
    ninfo2 = list(map(lambda a: lget_text(a.find('span',
                        class_='Boxscore__Athlete_Position')), peeps))
    ninfo3 = list(map(lambda a: lget_text(a.find('span',
                        class_='Boxscore__Athlete_Annotation')), peeps))
    return list(zip(list(zip(ninfo1, list(zip(ninfo2, ninfo3)))), stats))

def extract_data(binfo):
    """
    Grab all data from the html fragment.  Records will be generated later.
    """
    retv = table_fix(binfo)
    gloss_data = []
    glossary = binfo.find('div', class_='TeamGlossary')
    if glossary:
        gloss_data = glossary.get_text(separator='|', strip=False)
    extra_data = []
    extras = binfo.find_all('ul')
    if extras:
        elist  = list(map(lambda a: a.find_all('li'), extras))
        extras = list(chain.from_iterable(elist))
        headers = list(map(lget_text, list(map(lambda a: a.find('span'),
                                                  extras))))
        rdata = list(map(lambda a: a.text, extras))
        extra_data = list(filter(lambda a: a[0], list(zip(headers, rdata))))
        extra_data = list(map(lambda a: (a[0], a[1][len(a[0]):]), extra_data))
    subs = []
    sub_list = binfo.find_all('div', class_='pl4')
    if sub_list:
        subs = list(map(lambda a: a.get_text(separator='|', strip=False),
                        sub_list))
    return {'table': retv[1:-1], 'glossary': gloss_data,
            'extra': extra_data, 'subs': subs}
