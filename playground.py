from StatsDB import StatsDB
from IScraper import IScraper
import ids
import os
import pickle
import time
from render import render_last_race


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
    season_details = scraper.get_season_details(3478)
    race_week = None

    if race_week is None:
        # get highest raceweek
        race_week = max([x['race_week_num'] for x in season_details['results_list']])
    else:
        # correct index
        race_week = race_week - 1

    # get subsession ids for correct week
    subsession_ids = [x["subsession_id"] for x in season_details['results_list'] if x["race_week_num"] == race_week]

    car = scraper.get_car_details()
    carclass = scraper.get_carclass_details()

    # get results for subsessions
    for sid in subsession_ids:
        ss_info = scraper.get_subsession_details(sid)
        print()