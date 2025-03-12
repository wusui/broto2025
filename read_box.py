# Copyright (C) 2025 Warren Usui, MIT License
"""
Extract the boxscore data for one game
"""
from bs4 import BeautifulSoup
from io_interfaces import get_webpage, save_data
from extract_data import extract_data
from convert_data import convert_data

def read_box(number):
    """
    Read a box score, given it's number.  Return soup
    """
    box = get_webpage(f'https://www.espn.com/mlb/boxscore/_/gameId/{number}')
    return BeautifulSoup(box, "html.parser")

def get_score(in_text, visitor, home):
    """
    Extract score as dict indexed by team abbreviation
    """
    def gscore(dside):
        parts = in_text.text.split(f'{dside}Side')
        nscore = parts[1][:parts[1].find(',')]
        return int(nscore[nscore.rfind(':') + 1:])
    return {visitor: gscore('left'), home: gscore('right')}

def wls_data(ind_data):
    """
    Extract Win, Loss, Hold, Save, Blown Save info for game.
    """
    def just_get_stt(pstat_str):
        prts = list(map(lambda a: a.strip(), pstat_str.split(",")))
        return list(filter(lambda a: len(a) == 1 and a.isupper(), prts))
    def wls_inner(indx):
        pitn = parts[indx][parts[indx].rfind('shrtNm'):].split('"')[2]
        result = parts[indx + 1].split('"')[2:4]
        return (pitn, just_get_stt(result[0]))
    if len(ind_data) == 0:
        return []
    parts = ind_data[0].text.split('ptchNt')
    return list(map(wls_inner, range(len(parts) - 1)))

def read_game_info(game_no):
    """
    Input box score number, return dict indexed by game team codes.
    Each dict value is a list of player records (batting, pitching)
    Score and Won/Loss stats are scraped from a script tag.
    """
    gamed = read_box(game_no)
    gtitle = gamed.find('title').text
    print(gtitle)
    visitor = gamed.find_all('th', class_='playByPlay__awayTeam')
    if not visitor:
        return visitor
    visitor = visitor[0].text
    home = gamed.find_all('th', class_='playByPlay__homeTeam')[0].text
    boxscore = gamed.find('div', class_='Boxscore')
    pit_bat = boxscore.find_all('div', class_='Boxscore__Category')
    bat_dat = pit_bat[0].find_all('div', class_='Boxscore__Team')
    pit_dat = pit_bat[1].find_all('div', class_='Boxscore__Team')
    ind_data = list(filter(lambda a: 'ptchNt' in a.text,
                    gamed.find_all('script')))
    if len(ind_data) == 0:
        score = {visitor: 100, home: 100}
    else:
        score = get_score(ind_data[0], visitor, home)
    return {visitor: [extract_data(bat_dat[0]), extract_data(pit_dat[0])],
              home: [extract_data(bat_dat[1]), extract_data(pit_dat[1])],
              'score': score, 'pit_data': wls_data(ind_data),
              'one_line': gtitle}

def get_game_info(game_no):
    """
    Wrapper that extracts raw data and converts it
    """
    info = convert_data(read_game_info(game_no))
    if not info:
        return []
    return info[0][0] + info[0][1] + info[1][0] + info[1][1]

if __name__ == "__main__":
    save_data(get_game_info('401704401'), 'INFO1')
