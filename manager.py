import sys
import os
import time
import json
import ast
import wanikani_api.exceptions

from wanikani_api.client import Client as WaniKaniClient
from argh import dispatch_commands, arg

def create_profile(api_key, users_fp='users.json'):
    client = WaniKaniClient(api_key)

    user_information = client.user_information()
    start_date = user_information.started_at.strftime('%B %d, %Y')
    print(f'Hi {user_information.username}!')
    print(f'You started WaniKani on {start_date}')
    print(f'and are currently level {user_information.level}')
    
    new_user = dict(
        username=user_information.username,
        api_key=api_key,
        modes=dict(
            reverse_kani=dict(
                history=dict(),
                content=dict()
            )
        )
    )

    users = {'users': []}
    if os.path.isfile(users_fp):
        with open(users_fp, 'r') as f:
            users = json.load(f)

    num_users = len(users['users'])
    print(f'Found {num_users} existing users')

    existing_user = False
    for user_idx in range(len(users['users'])):
        curr_user = users['users'][user_idx]
        if curr_user['username'] == user_information.username:
            existing_user = True
            print(f'User with {user_information.username} already found, performing minimal updates')
            curr_user['api_key'] = api_key

    if not existing_user:
        users['users'].append(new_user)

    print(f'Saving users to {users_fp}...', end='')
    with open(users_fp, 'w') as f:
        json.dump(users, f, indent=2)
    print('Done', end='\n\n')

    return new_user

def update_dictionary(api_key, dict_fp='dictionary.json'):
    client = WaniKaniClient(api_key)

    print('Downloading dictionary...', end='')
    vocab_list = []
    for vocab in client.subjects(types='vocabulary', fetch_all=True):
        vocab_list.append(ast.literal_eval(vocab.raw_json()))

    kanji_list = []
    for kanji in client.subjects(types='kanji', fetch_all=True):
        kanji_list.append(ast.literal_eval(kanji.raw_json()))

    new_dictionary = dict(
        vocabulary=vocab_list,
        kanji=kanji_list
    )
    print('Done')

    old_dictionary = dict(
        vocabulary=[],
        kanji=[]
    )
    if os.path.isfile(dict_fp):
        with open(dict_fp, 'r') as f:
            old_dictionary = json.load(f)

    vocab_diff = len(new_dictionary['vocabulary']) - len(old_dictionary['vocabulary'])
    kanji_diff = len(new_dictionary['kanji']) - len(old_dictionary['kanji'])
    print(f'Found {vocab_diff} new vocabulary!')
    print(f'Found {kanji_diff} new kanji!')

    # Save the new dictionary
    print(f'Saving dictionary to {dict_fp}...', end='')
    with open(dict_fp, 'w') as f:
        json.dump(new_dictionary, f, indent=2)
    print('Done', end='\n\n')

    return new_dictionary

def initial_setup(
    advanced: 'Enable advanced configuration mode'=False
):
    print('Running first time setup...')

    print('Please obtain API token from https://www.wanikani.com/settings/personal_access_tokens')
    while True:
        api_key = input('Enter token here: ').strip()

        try:
            client = WaniKaniClient(api_key)
            user_info = client.user_information()
            break
        except wanikani.exceptions.InvalidWanikaniApiKeyException:
            print('Invalid API key!')
        
    print('Connected to the WaniKani API!', end='\n\n')
    cwd = os.getcwd()

    # Create the user
    if advanced:
        while True:
            users_fp = input(f'Enter users.json location [Default={cwd}]: ').strip()
            if users_fp == '':
                users_fp = cwd

            if os.path.isdir(users_fp):
                break

            print('Invalid directory!')
    else:
        users_fp = cwd
    users_fp = os.path.join(users_fp, 'users.json')
    user = create_profile(api_key, users_fp)
    username = user['username']

    # Create the dictionary
    if advanced:
        while True:
            dict_fp = input(f'Enter dictionary.json location [Default={cwd}]: ').strip()
            if dict_fp == '':
                dict_fp = cwd

            if os.path.isdir(dict_fp):
                break

            print('Invalid directory!')
    else:
        dict_fp = cwd
    dict_fp = os.path.join(dict_fp, 'dictionary.json')
    update_dictionary(api_key, dict_fp)

    print('Setup complete, enjoy WaniMoreKani!')
    print('Run with the following command:', end='\n\n')
    print(f'python gui.py {username} --users-fp {users_fp} --dict-fp {dict_fp}', end='\n\n')

if __name__ == '__main__':
    dispatch_commands([initial_setup])





