from StatsDB import StatsDB
from IScraper import IScraper
import ids
import os
import pickle
import time
from render import render_last_race

os.environ['ir_user'] = 'max.uppenkamp@rwth-aachen.de'
os.environ['ir_password'] = 'LjNF(;Al9zO|%5-EZ=y.'


def scrape_all():
    # main
    series_data = {}
    scraper = IScraper()

    for series, season_id in ids.season_ids.items():
        print(f'Grabbing {series}')
        weekly_sessions = scraper.get_sessions_for_season(season_id)
        series_data[series] = weekly_sessions

    return series_data


def reload_backup():
    with open('backup.pickle', 'rb') as inf:
        series_data = pickle.load(inf)
    return series_data


def crawl(series):
    series_data = reload_backup()

    # insert into DB
    db = StatsDB('stats.db')
    for s in series:
        print(s)
        time.sleep(60)
        for week, week_data in series_data[s].items():
            print(f'\t{week}')
            time.sleep(10)
            db.insert_series_data(week_data)


def render_test():
    db = StatsDB('stats.db')
    race_info = db.last_race_info('Jan+Gebhardt')
    print(render_last_race(race_info))


if __name__ == "__main__":
    scraper = IScraper()
    rr = scraper.get_series_meta()
    print(rr)
