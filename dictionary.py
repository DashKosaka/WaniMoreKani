import os
import ast
import json

from wanikani_api.client import Client as WaniKaniClient

def get_review_material(user, dict_fp='dictionary.json'):
    api_key = user['api_key']

    client = WaniKaniClient(api_key)

    user_information = client.user_information()
    user_level = user_information.level

    with open(dict_fp, 'r') as f:
        dictionary = json.load(f)

    vocabulary = dictionary['vocabulary']

    filtered_vocab = []
    for vocab_json in vocabulary:
        if vocab_json['data']['level'] > user_level:
            continue    

        filtered_vocab.append(vocab_json)

    temp_dict = {}
    for vocab_json in filtered_vocab:
        subject_id = vocab_json['id']

        temp_dict[subject_id] = vocab_json['data']

    subject_ids = list(temp_dict.keys())
    MAX_QUERY_SIZE = 500
    review_dict = {}
    for start_idx in range(0, len(subject_ids), MAX_QUERY_SIZE):
        subjects_slice = subject_ids[start_idx:start_idx + MAX_QUERY_SIZE]

        stats = client.review_statistics(subject_ids=subjects_slice)
        for stat in stats:

            # if stat.hidden == True:
            #     continue
                
            # TODO: Figure out logic to figure out if studied already

            review_dict[stat.subject_id] = temp_dict[stat.subject_id]

    # for vocab in filtered_vocab:
    #     print([m['meaning'] for m in vocab['meanings']], vocab['slug'], [r['reading'] for r in vocab['readings']])


    print(f'Dictionary length: {len(vocabulary)}')
    print(f'Level filtering: {len(filtered_vocab)}')
    print(f'Temp: {len(temp_dict)}')
    print(f'Final word count: {len(review_dict)}')

    return filtered_vocab


def get_meaning(info, idx=0):
    return info['data']['meanings'][idx]['meaning']

def get_num_meanings(info):
    return len(info['data']['meanings'])

def get_reading(info, idx=0):
    return info['data']['readings'][idx]['reading']

def get_num_readings(info):
    return len(info['data']['readings'])

def get_object_type(info):
    return info['object']

def get_id(info):
    return str(info['id'])

if __name__ == '__main__':

    material = get_review_material()
    import random

    test_results = {}
    random.shuffle(material)
    for vocab in material:
        try:
            vocab_data = vocab['data']
            vocab_meaning = vocab_data['meanings'][0]['meaning']
            vocab_slug = vocab_data['slug']
            print(f'Vocab: \"{vocab_meaning}\" = ', end='')
            answer = input()
            if vocab_slug == answer or any([r['reading'] == answer for r in vocab_data['readings']]):
                print('Correct!')
                test_results[vocab['id']] = test_results.get(vocab['id'], 0) + 1
            else:
                print(f'Incorrect...the correct answer is {vocab_slug}')
                test_results[vocab['id']] = test_results.get(vocab['id'], 0) - 1

        except KeyboardInterrupt:
            break

    for vocab_id in test_results:
        print(f'{vocab_id}: {test_results[vocab_id]}')






