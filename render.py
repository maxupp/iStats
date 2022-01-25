import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def deplus(s):
    return s.replace('+', ' ')


def participation_or_sof(season_details, p_or_s, series_name):
    df = pd.DataFrame.from_records(season_details['results_list'])
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['weekday'] = df['start_time'].dt.weekday
    df['daytime'] = df['start_time'].dt.time

    # data kungfu
    if p_or_s == 'p':
        grouped = df.groupby(['weekday', 'daytime']).agg({'num_drivers': ['mean']})
    elif p_or_s == 's':
        grouped = df.groupby(['weekday', 'daytime']).agg({'event_strength_of_field': ['max']})
    participation = grouped.unstack('daytime')
    participation.index = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    participation.columns = [x[2] for x in participation.columns]

    # render
    plt.figure(figsize=(12, 4))
    title = 'Participation' if p_or_s == 'p' else 'Strength of Field'
    title += f': {series_name}'
    sns.heatmap(participation, cmap="YlGnBu", annot=True, fmt='g').set(title=title)

    temp_image_name = 'temp.png'
    plt.savefig('temp.png', bbox_inches='tight')

    return temp_image_name


def schedule(schedules):
    tracks = [x['track']['track_name'] + ' ' + x['track'].get('config_name', '') for x in schedules]
    ret = f'Schedule: {schedules[0]["season_name"]}\n'
    for i, t in enumerate(tracks, start=1):
        ret += f'\tWeek {i}: \t{t}\n'
    return ret


def render_last_race(race_info):
    ret = ''
    ret += f'Track: {deplus(race_info["track_name"])}\n'
    ret += f'Driver: {deplus(race_info["display_name"])}\n'
    ret += f'SoF: {race_info["strength_of_field"]}\n'
    ret += f'Incidents: {race_info["incidents"]}\n'
    diff = race_info["new_irating"] - race_info["old_irating"]
    ret += f'iRating: {race_info["new_irating"]} ({diff})\n'
    ret += f'Fastest Lap: {race_info["best_laptime"]}\n'
    return ret
