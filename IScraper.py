import requests
import time
import os


class IScraper:
    def __init__(self):
        self.user = os.environ['ir_user']
        self.password = os.environ['ir_password']
        self.session = requests.Session()

    def auth(self):
        r = self.session.post('https://members-ng.iracing.com/auth',
                          data={
                              'email': self.user,
                              'password': self.password
                          })
        return r

    def request_wrapper(self, functor, args):
        response = functor(**args)
        if response.status_code == 401:
            print('Logging into iRacing website...')
            self.auth()
            response = functor(**args)

        # retrieve bucket
        bucket_url = response.json()['link']
        response = self.session.get(bucket_url)

        if response.status_code != 200:
            print(f'Request failed')

        return response.json()

    def get_driver_recent_races(self, driver):
        url = f'https://members-ng.iracing.com/data/stats/member_recent_races?cust_id={driver}'
        response = self.request_wrapper(self.session.get, {'url': url})

        return response

    def get_driver_career(self, driver):
        url = f'https://members-ng.iracing.com/data/stats/member_career?cust_id={driver}'
        response = self.request_wrapper(self.session.get, {'url': url})

        return response

    def get_subsession_details(self, subsession_id):
        url = f'https://members-ng.iracing.com/data/results/get?subsession_id={subsession_id}'
        response = self.request_wrapper(self.session.get, {'url': url})

        return response

    def get_series_meta(self):
        url = 'https://members-ng.iracing.com/data/series/seasons'
        response = self.request_wrapper(self.session.get, {'url': url})

        return response

    def get_season_details(self, season_id):
        url = f'https://members-ng.iracing.com/data/results/season_results?season_id={season_id}&event_type=5'
        response = self.request_wrapper(self.session.get, {'url': url})

        return response

    def get_car_details(self):
        url = f'https://members-ng.iracing.com/data/car/get'
        response = self.request_wrapper(self.session.get, {'url': url})

        return response

    def get_carclass_details(self):
        url = f'https://members-ng.iracing.com/data/carclass/get'
        response = self.request_wrapper(self.session.get, {'url': url})

        return response


