# Copyright (C) 2025 Warren Usui, MIT License
"""
Extract the boxscore data for all games on one day
"""
from datetime import datetime, timedelta
import itertools
from bs4 import BeautifulSoup
import pandas
from io_interfaces import get_webpage, save_data
from read_box import get_game_info

def get_game_ids(in_date):
    """
    Scrape the schedule page for game ids
    """
    url = f'https://www.espn.com/mlb/schedule/_/date/{in_date}'
    response = get_webpage(url)
    soup = BeautifulSoup(response, 'html.parser')
    tables = soup.find_all('div', class_='ResponsiveTable')
    links = tables[0].find_all('a', class_='AnchorLink', href=True)
    glinks = list(filter(lambda a: 'gameId' in a['href'], links))
    game_inf = list(map(lambda a: a['href'], glinks))
    return list(map(lambda a: a.split('/')[-2], game_inf))

def text_to_date(in_text):
    """
    Convert date input (m/d/yyyy) to format used on ESPN urls
    """
    if in_text[0].isalpha():
        gday = datetime.now() - timedelta(days=8)
    else:
        gday = datetime.strptime(in_text, "%m/%d/%Y")
    return gday.strftime('%Y%m%d')

def get_day(in_date):
    """
    Main entry point wrapper
    """
    return get_game_ids(text_to_date(in_date))

def yesterday():
    """
    Special case to handle yesterday's games
    """
    games = list(map(get_game_info, get_day('yesterday')))
    oinfo = text_to_date('yesterday')
    all_data = list(itertools.chain.from_iterable(games))
    save_data(all_data, oinfo)

def find_range(dfrom, dto):
    """
    Select a date range for games to be saved.
    """
    def fr_func(one_day):
        games = list(map(get_game_info, get_game_ids(one_day[0])))
        all_data = list(itertools.chain.from_iterable(games))
        save_data(all_data, one_day[1])
    ptimes = list(pandas.date_range(start=dfrom, end=dto))
    dtimes = list(map(lambda a: a.to_pydatetime().strftime('%Y%m%d'), ptimes))
    drange = list(map(lambda a: a.split()[0].replace('-', ''),
                      list(map(str, ptimes))))
    bundle = list(zip(dtimes, drange))
    list(map(fr_func, bundle))

if __name__ == "__main__":
    find_range('2025-02-27', '2025-03-10')
