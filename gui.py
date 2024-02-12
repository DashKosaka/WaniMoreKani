import dictionary
import dictionary as d
import json
import random
import time

from argh import dispatch_command, arg
from dash import Dash, dcc, html, ctx, callback, Input, Output, State
from dash.exceptions import PreventUpdate

def get_random_word(user, material):
    num_material = len(material)

    rand_idx = random.randint(0, num_material - 1)
    rand_key = list(material.keys())[rand_idx]
    return material[rand_key]

def populate_session(user, material, srs, mode='reverse_kani'):

    available_material = {}

    user_content = user['modes'][mode]['content']
    for info in material:
        material_id = d.get_id(info)

        content = user_content.get(material_id, None)

        # Add content
        if content is None:
            available_material[material_id] = info
            user_content[material_id] = {'position': 1, 'last_correct_timestamp': 0}
        else:
            position = content['position']
            last_correct_timestamp = content['last_correct_timestamp'] // (60 * 60) * (60 * 60)
            # print(position, last_correct_timestamp)

            position_info = srs['stages'][position]
            if position_info['interval_unit'] != 'seconds':
                raise ValueError('Found unsupported srs interval_unit')

            downtime = position_info['interval'] 
            curr_timestamp = time.time() // (60 * 60) * (60 * 60)

            # Only add to available material if enough time has passed
            if curr_timestamp - last_correct_timestamp > downtime:
                available_material[material_id] = info

    return available_material

@callback(
    Output('review-info', 'data'),
    Output('review', 'children'),
    Output('review-type', 'children'),
    Output('review-readings', 'children'),

    Output('store-material', 'data'),
    Output('users-info', 'data'),
    Output('srs', 'data'),
    Output('session-feedback', 'data'),

    Output('num-remaining', 'children'),

    Input('div-reset', 'children'),

    State('username', 'children'),
    State('dict-fp', 'children'),
    State('users-fp', 'children'),
    State('srs-fp', 'children'),
    State('session-mode', 'children'),

)
def initialize(
    reset,

    username,
    dict_fp,
    users_fp,
    srs_fp,
    session_mode
):

    # Get the user information
    with open(users_fp, 'r') as f:
        users = json.load(f)

    curr_user = users['users'][0]
    for user in users['users']:
        if user['username'] == username:
            curr_user = user

    # Get the srs
    with open(srs_fp, 'r') as f:
        srs = json.load(f)

    # Get the dictionary
    material = dictionary.get_review_material(user, dict_fp)
    available_material = populate_session(curr_user, material, srs)

    info = get_random_word(curr_user, available_material)

    meaning = d.get_meaning(info)
    object_type = d.get_object_type(info)
    num_readings = d.get_num_readings(info)
    return info, meaning, object_type.capitalize(), num_readings, available_material, users, srs, {12341234: 'nice'}, len(available_material)

@callback(
    Output('review-info', 'data', allow_duplicate=True),
    Output('review', 'children', allow_duplicate=True),
    Output('review-type', 'children', allow_duplicate=True),
    Output('input-answer', 'value'),

    Output('store-material', 'data', allow_duplicate=True),

    Output('num-correct', 'children', allow_duplicate=True),
    Output('num-answered', 'children', allow_duplicate=True),
    Output('num-remaining', 'children', allow_duplicate=True),

    # Static information
    State('review-info', 'data'),
    State('review', 'children'),
    State('review-type', 'children'),
    State('username', 'children'),

    # 
    Input('input-answer', 'n_submit'),
    Input('button-submit', 'n_clicks'),
    State('input-answer', 'value'),

    State('store-material', 'data'),
    State('users-info', 'data'),
    State('session-feedback', 'data'),
    State('users-fp', 'children'),

    State('num-correct', 'children'),
    State('num-answered', 'children'),

    prevent_initial_call=True
)
def submit_answer(
    info,
    review,
    review_type,
    username,

    enter,
    submit,
    answer,

    available_material,
    users,
    session_feedback,
    users_fp,

    num_correct,
    num_answered
    
):

    num_correct = int(num_correct)
    num_answered = int(num_answered)

    # Check if a word needs to be initialized
    # if review_type == '' or review == '':
    #     material = dictionary.get_review_material('dictionary.json')

    #     # Get the user information
    #     with open('users.json', 'r') as f:
    #         users = json.load(f)['users'][0]
    #     info = get_random_word(users, material)

    #     meaning = d.get_meaning(info)
    #     object_type = d.get_object_type(info)
    #     return info, object_type.capitalize(), meaning, ''

    if answer == '':
        raise PreventUpdate

    if not (ctx.triggered_id == 'input-answer' or ctx.triggered_id == 'button-submit') or (enter == 0 and submit == 0):
        raise PreventUpdate

    # TODO: Interpret answer


    # Check if answer matches
    reading = d.get_reading(info)
    object_type = d.get_object_type(info)
    correct = answer == reading

    # Generate a new prompt
    material_id = str(d.get_id(info))
    if correct:
        print('Correct')
        available_material.pop(material_id)
        # TODO

        if session_feedback.get(material_id, None) is None:
            users['users'][0]['modes']['reverse_kani']['content'][material_id]['position'] += 1
        else:
            users['users'][0]['modes']['reverse_kani']['content'][material_id]['position'] -= 1

        users['users'][0]['modes']['reverse_kani']['content'][material_id]['last_correct_timestamp'] = time.time()
        print('Saving to', users_fp)
        with open(users_fp, 'w') as f:
            json.dump(users, f, indent=2)
        print('Done')
    else:
        print('Incorrect:', answer, reading)
        curr_feedback = session_feedback.get(material_id, {'num-misses': 1})
        session_feedback[material_id] = curr_feedback

    info = get_random_word(None, available_material)
    meaning = d.get_meaning(info)
    object_type = d.get_object_type(info)

    return info, meaning, object_type.capitalize(), '', available_material, num_correct + correct, num_answered + 1, len(available_material)

@arg('--mode', choices=['reverse_kani'])
def setup(
    username: 'Username of the current user',
    dict_fp: 'Path to the dictionary files'='dictionary.json',
    users_fp: 'Path to the user profiles'='users.json',
    srs_fp: 'Path to the spaced repetition system'='srs.json',
    mode: 'Session mode'='reverse_kani'
):
    # material = dictionary.get_review_material(dict_fp)
    with open(users_fp, 'r') as f:
        users = json.load(f)

    user = users['users'][0]

    app = Dash(__name__)


    session_info = html.Div([
        html.Div([
            'Username: ',
            html.B(f'{username}', id='username')
        ], style={'color': 'black', 'font-size': '20px', 'padding-block': '5px'}),
        html.Div([
            'Score: ',
            html.B('0', id='num-correct'),
            ' / ',
            html.B('0', id='num-answered')
        ], style={'color': 'black', 'font-size': '20px', 'padding-block': '5px'}),
        html.Div([
            'Remaining: ',
            html.B(f'0', id='num-remaining')
        ], style={'color': 'black', 'font-size': '20px', 'padding-block': '5px'})
    ])

    app.layout = html.Div([
        html.Div([
                html.Div(id='review', style={'color': 'white', 'font-size': '80px', 'background-color': '#AA00FF', 'background': 'linear-gradient(#AA00FF, #9300DD)','padding-block': '20px'}),
                html.Div([
                    html.Div([
                        html.P(id='review-type', style={'display': 'inline'}),
                        html.B(' Reading')
                    ], style={'color': 'black', 'font-size': '30px', 'padding-block': '5px'}),
                    html.Div([
                        'Accepted Answers: ',
                        html.B(id='review-readings')
                    ], style={'color': 'black', 'font-size': '20px', 'padding-block': '5px'}),
                ], style={'background': 'linear-gradient(#EEEEEE, #E0E0E0)'})
        ]),
        html.Div([
                dcc.Input(id='input-answer', placeholder='Answer here...', type='text', value='', debounce=False),
                html.Button('Submit', id='button-submit', n_clicks=0),

        ], style={'padding-block': '10px'}),
        html.Div(id='div-feedback',),
        html.Div(id='div-reset'),

        session_info,

        html.P(f'{dict_fp}', id='dict-fp', style={'display': 'none', 'background-color': '#AA0000'}),
        html.P(f'{users_fp}', id='users-fp', style={'display': 'none', 'background-color': '#AA0000'}),
        html.P(f'{srs_fp}', id='srs-fp', style={'display': 'none', 'background-color': '#AA0000'}),
        html.P(f'{mode}', id='session-mode', style={'display': 'none', 'background-color': '#AA0000'}),
        dcc.Store(id='store-material'),
        dcc.Store(id='users-info'),
        dcc.Store(id='srs'),
        dcc.Store(id='review-info'),
        dcc.Store(id='session-feedback')
    ], style={'text-align': 'center'})

    app.run(debug=True, port=8051)


# Start app
# Load the userdata, or cache username
# Get the user information
# Load the possible review materials based on the user
# When generating a new word
#   Take the possible review materials
#   Enumerate each review material
#   Sample the review material
#   Check if the review material is in the user's material list
#   If it isn't, use it as material
#   If it is, check if it is free to test time-wise
#   Wait for an answer
#   After an answer, update 


if __name__ == '__main__':
    dispatch_command(setup)
