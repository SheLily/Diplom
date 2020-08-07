import requests
import json
from datetime import datetime


class VKinder:
    def __init__(self, token, v='5.107'):
        self.token = token
        self.v = v
        self.base_config = {
            'access_token': self.token,
            'v': self.v
        }
        (
            self.id,
            self.sex,
            self.year,
            self.city,
            self.relation
            ) = self.get_info()
        self.handle_bdate()

        try:
            from pymongo import MongoClient
            import pymongo
            self.connect = MongoClient()
            self.db = self.connect['local-database']
            self.db = self.db['test-collecction']
            self.save_to_db = True
        except:
            print('BD is unavailable. Results will not be saved')
            self.save_to_db = False

    def get_info(self):
        method = 'users.get'
        url = f'https://api.vk.com/method/{method}'
        config = self.base_config.copy()
        config['fields'] = 'bdate,sex,city,relation'
        result = requests.get(url, config).json()
        result = result['response'][0]
        return (
            result['id'],
            result['sex'],
            result['bdate'],
            result['city']['id'],
            result['relation']
            )

    def handle_bdate(self):
        self.year = self.year.split('.')
        if len(self.year) == 2:
            self.year = input('Введите год рождения')
        else:
            self.year = self.year[-1]

    def do(self):
        if self.save_to_db:
            viewed = {
                i['view_id'] for i in self.db.posts.find({'main_id': self.id})
                }
        else:
            viewed = {}
        method = 'users.search'
        url = f'https://api.vk.com/method/{method}'
        config = self.base_config.copy()
        config['city'] = self.city
        config['sex'] = 1 if self.sex == 2 else 2
        config['status'] = '6'
        config['birth_year'] = self.year
        config['count'] = 1000
        result = requests.get(url, config).json()['response']['items']
        result = [i for i in result if not i['is_closed']]
        if len(viewed) != 0:
            result = [i for i in result if i['id'] not in viewed]
        result = result[:10]
        for i in result:
            method = 'photos.get'
            url = f'https://api.vk.com/method/{method}'
            config = self.base_config.copy()
            config['owner_id'] = i['id']
            config['album_id'] = 'profile'
            config['extended'] = 1
            photos = requests.get(url, config).json()
            photos = photos['response']['items']
            photos.sort(key=lambda x: x['likes']['count'])
            i['photos'] = [photo['sizes'][-1]['url'] for photo in photos[:3]]

        if self.save_to_db:
            for i in result:
                self.db.posts.insert_one(
                    {
                        'main_id': self.id,
                        'view_id': i['id'],
                        'photos': i['photos']
                        }
                    )
        result = [
            {
                'url': f'https://vk.com/id{i["id"]}',
                'photos': i['photos']
            } for i in result
            ]
        with open(
                (f'{self.id} ',
                 f'{str(datetime.now()).replace(":", " ")}.json'), 'w') as fp:
            json.dump(result, fp)
        return result
