#!/usr/bin/env python3
import json

'''
Usage:
Download Arcaea apk from official website and extrace songlist and packlist here,
Then run this script:


Structure:
songlist = [
    {
        'id' : str,
        "title": str,
        "title_ja": str,
        "set": str,
        "levels": [pst, prs, ftr]，
        "constants": [pst, prs, ftr]
    }, ...
]

songlist_by_set = [
    {
        'set_name': [
            {
                <songs>
            }, ...
        ],
        'set_name': [
            {
                <songs>
            }
        ]
    }
]
'''
complete = json.load(open('songlist'))
packs = json.load(open('packlist'))
converted = []
converted_by_set = {}
id_list = []
packlist = [{'id': 'single', 'title': 'Memory Archive'}]
packids = []


for song in complete['songs']:
    id_list.append(song['id'])
    converted.append(
        {
            'id': song['id'],
            'title': song['title_localized']['en'],
            'title_ja': '' if 'ja' not in song['title_localized'].keys() else song['title_localized']['ja'],
            'set': song['set'],
            'levels': [
                str(song['difficulties'][0]['rating']),
                str(song['difficulties'][1]['rating']),
                '9+' if song['difficulties'][2]['rating'] == 10 else '10' if song['difficulties'][2]['rating'] == 11 else str(song['difficulties'][2]['rating'])
            ],
            'unlock': True if 'world_unlock' in song.keys() else False     # 是否需要在世界模式解锁，需要则为 True, 不需要则为 False
        }
    )
    if song['set'] not in converted_by_set.keys():
        converted_by_set[song['set']] = []
    
    converted_by_set[song['set']].append(
        {
            'id': song['id'],
            'title': song['title_localized']['en'],
            'title_ja': '' if 'ja' not in song['title_localized'].keys() else song['title_localized']['ja'],
            'set': song['set'],
            'levels': [
                str(song['difficulties'][0]['rating']),
                str(song['difficulties'][1]['rating']),
                '9+' if song['difficulties'][2]['rating'] == 10 else '10' if song['difficulties'][2]['rating'] == 11 else str(song['difficulties'][2]['rating'])
            ]
        }
    )
    
for pack in packs['packs']:
    packlist.append({
        'id': pack['id'],
        'title': pack['name_localized']['en']   
    })
    packids.append(pack['id'])


songlist = open('Songlist.py', 'w+')
songlist.write('songlist = ' + str(converted) + '\n')
songlist.write('songlist_by_set = ' + str(converted_by_set) + '\n')
songlist.write('songs_by_id = ' + str(id_list) + '\n')
songlist.write('packlist = ' + str(packlist) + '\n')
songlist.write('packid_list = ' + str(packids) + '\n\n')
songlist.close()

