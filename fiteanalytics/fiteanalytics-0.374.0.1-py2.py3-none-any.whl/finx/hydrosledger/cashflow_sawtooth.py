# *****************************************************
# * FinX is a set of tools for Financial Data Science *
# * Copyright (C) 2017  Fite Analytics LLC            *
# *****************************************************
#
# This file is part of FinX.
#
#     FinX is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     FinX is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with FinX.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import base64
import bz2
import inspect
import json
import numpy as np
import random
import pandas as pd
import requests
from dateutil.parser import parse as dtparse
import plotly.graph_objs as go
from IPython.display import display, HTML
from plotly.offline import init_notebook_mode, iplot
from uuid import uuid4

from fiteanalytics.finx.admin.config import Config


def create_account(account_uuid,
                   account_model_type='generic account',
                   account_type=None,
                   account_name=None,
                   account_code=None,
                   owner_legal_entity_uuid=None,
                   initial_balance=None,
                   min_balance_limit=None,
                   max_balance_limit=None,
                   min_credit_amount_limit=None,
                   max_credit_amount_limit=None,
                   min_debit_amount_limit=None,
                   max_debit_amount_limit=None,
                   payload_datestamp=None,
                   tz=None,
                   dependencies=None,
                   nonce=None,
                   submit_batch=True):
    config = Config()
    sawtooth_data_uri = config.settings['endpoints']['hydrosledger']['hydrostp']
    sawtooth_data_uri += 'hydrosledger_account/create/'
    payload = dict(account_uuid=account_uuid,
                   account_model_type=account_model_type,
                   account_type=account_type,
                   account_name=account_name,
                   account_code=account_code,
                   owner_legal_entity_uuid=owner_legal_entity_uuid,
                   initial_balance=initial_balance,
                   min_balance_limit=min_balance_limit,
                   max_balance_limit=max_balance_limit,
                   min_credit_amount_limit=min_credit_amount_limit,
                   max_credit_amount_limit=max_credit_amount_limit,
                   min_debit_amount_limit=min_debit_amount_limit,
                   max_debit_amount_limit=max_debit_amount_limit,
                   payload_datestamp=str(payload_datestamp),
                   tz=tz,
                   dependencies=dependencies,
                   nonce=nonce,
                   submit_batch=submit_batch,
                   finx_key=config.settings['identity']['finx_key'])
    try:
        response = requests.get(sawtooth_data_uri, params=payload)
    except requests.exceptions.RequestException:
        response = None
        print('[x] Account not created due to server inaccessibility')
    if response is not None:
        response_dict = json.loads(response.text)
        if response.ok:
            if submit_batch is True:
                print('[✓] Account "{}" has been created'.format(account_uuid))
            else:
                return response_dict
        if response.status_code == 400:
            bad_request_params = response_dict['bad_request_params']
            for param_key in bad_request_params:
                if param_key == 'private_key':
                    print('[x] Account "{}" already exists'.format(account_uuid))
                elif param_key in payload:
                    print('[x] Specified {} "{}" is not valid'.format(param_key.replace('_', ' ').title(),
                                                                      payload[param_key]))
                else:
                    print('[x] {} is not valid'.format(param_key.replace('_', ' ').title()))
        elif response.status_code == 409:
            print('[x] Account not created due to transaction validation error')
        elif response.status_code == 500:
            print('[x] Account not created due to server error')


def edit_account(account_uuid,
                 account_type=None,
                 account_name=None,
                 account_code=None,
                 owner_legal_entity_uuid=None,
                 min_balance_limit=None,
                 max_balance_limit=None,
                 min_credit_amount_limit=None,
                 max_credit_amount_limit=None,
                 min_debit_amount_limit=None,
                 max_debit_amount_limit=None,
                 payload_datestamp=None,
                 tz=None,
                 dependencies=None,
                 nonce=None,
                 submit_batch=True):
    config = Config()
    sawtooth_data_uri = config.settings['endpoints']['hydrosledger']['hydrostp']
    sawtooth_data_uri += 'hydrosledger_account/edit/'
    payload = dict(account_uuid=account_uuid,
                   account_type=account_type,
                   account_name=account_name,
                   account_code=account_code,
                   owner_legal_entity_uuid=owner_legal_entity_uuid,
                   min_balance_limit=min_balance_limit,
                   max_balance_limit=max_balance_limit,
                   min_credit_amount_limit=min_credit_amount_limit,
                   max_credit_amount_limit=max_credit_amount_limit,
                   min_debit_amount_limit=min_debit_amount_limit,
                   max_debit_amount_limit=max_debit_amount_limit,
                   payload_datestamp=str(payload_datestamp),
                   tz=tz,
                   dependencies=dependencies,
                   nonce=nonce,
                   submit_batch=submit_batch,
                   finx_key=config.settings['identity']['finx_key'])
    try:
        response = requests.get(sawtooth_data_uri, params=payload)
    except requests.exceptions.RequestException:
        response = None
        print('[x] Account not edited due to server inaccessibility')
    if response is not None:
        response_dict = json.loads(response.text)
        if response.ok:
            if submit_batch is True:
                print('[✓] Account "{}" has been edited'.format(account_uuid))
            else:
                return response_dict
        if response.status_code == 400:
            bad_request_params = response_dict['bad_request_params']
            for param_key in bad_request_params:
                if param_key == 'private_key':
                    print('[x] Account "{}" does not exist'.format(account_uuid))
                elif param_key in payload:
                    print('[x] Specified {} "{}" is not valid'.format(param_key.replace('_', ' ').title(),
                                                                  payload[param_key]))
                else:
                    print('[x] {} is not valid'.format(param_key.replace('_', ' ').title()))
        elif response.status_code == 409:
            print('[x] Account not edited due to transaction validation error')
        elif response.status_code == 500:
            print('[x] Account not edited due to server error')


def get_account(account_uuid,
                delta_type=None,
                start_date=None,
                as_of_date=None,
                max_count=None,
                all_states=None,
                order_by_earliest=None,
                tz=None):
    config = Config()
    sawtooth_data_uri = config.settings['endpoints']['hydrosledger']['hydrostp']
    sawtooth_data_uri += 'hydrosledger_account/state/'
    payload = dict(account_uuid=account_uuid,
                   delta_type=delta_type,
                   start_date=start_date,
                   as_of_date=as_of_date,
                   max_count=max_count,
                   all_states=all_states,
                   order_by_earliest=order_by_earliest,
                   tz=tz,
                   finx_key=config.settings['identity']['finx_key'])
    try:
        response = requests.get(sawtooth_data_uri, params=payload)
    except requests.exceptions.RequestException:
        response = None
        print('[x] No Account state(s) retrieved due to server inaccessibility')
    if response is not None:
        response_dict = json.loads(response.text)
        if response.status_code == 200:
            states = response_dict
            head_state = states[0]
            print("-----------ACCOUNT INFO (OF HEAD STATE)-----------")
            print("* account uuid = {}".format(head_state['account_uuid']))
            print("* account type = {}".format(head_state['account_type']))
            print("* account name = {}".format(head_state['account_name']))
            print("* account code = {}".format(head_state['account_code']))
            print("* owner legal entity uuid = {}".format(head_state['owner_legal_entity_uuid']))
            print("* journal entry uuid = {}".format(head_state['journal_entry_uuid']))
            print("* transaction uuid = {}".format(head_state['transaction_uuid']))
            print("* units = {}".format(head_state['units']))
            print("* unit amount = {}".format(head_state['unit_amount']))
            print("* unit price = {}".format(head_state['unit_price']))
            print("* credit amount = {}".format(head_state['credit_amount']))
            print("* debit amount = {}".format(head_state['debit_amount']))
            print("----------------------------------------------------")
            print("*** BALANCE = {}".format(head_state['balance']))
            print("----------------------------------------------------")
            df = pd.DataFrame(states)
            df['payload_datestamp'] = df['payload_datestamp'].apply(lambda x: dtparse(x))
            df.set_index('payload_datestamp', inplace=True)
            return df
        elif response.status_code == 204:
            print('[x] No state data exists for Account "{}"'.format(account_uuid))
        elif response.status_code == 400:
            bad_request_params = response_dict['bad_request_params']
            for param_key in bad_request_params:
                if param_key == 'private_key':
                    print('[x] Account "{}" does not exist'.format(account_uuid))
                elif param_key in payload:
                    print('[x] Specified {} "{}" is not valid'.format(param_key.replace('_', ' ').title(),
                                                                      payload[param_key]))
                else:
                    print('[x] {} is not valid'.format(param_key.replace('_', ' ').title()))
        elif response.status_code == 500:
            print('[x] Account state(s) not retrieved due to server error')
        return None


def xx(a=1,
       b=2,
       c=3,
       **d):
    pass
def get_accounts(*account_uuids,
                 delta_type=None,
                 start_date=None,
                 as_of_date=None,
                 max_count=None,
                 all_states=None,
                 order_by_earliest=None,
                 tz=None):
    config = Config()
    sawtooth_data_uri = config.settings['endpoints']['hydrosledger']['hydrostp']
    sawtooth_data_uri += 'hydrosledger_account/state/'

    df_list = list()
    for account_uuid in account_uuids:
        payload = dict(account_uuid=account_uuid,
                       delta_type=delta_type,
                       start_date=start_date,
                       as_of_date=as_of_date,
                       max_count=max_count,
                       all_states=all_states,
                       order_by_earliest=order_by_earliest,
                       tz=tz,
                       finx_key=config.settings['identity']['finx_key'])
        try:
            response = requests.get(sawtooth_data_uri, params=payload)
        except requests.exceptions.RequestException:
            response = None
            print('[x] No Account state(s) retrieved due to server inaccessibility')
        if response is not None:
            response_dict = json.loads(response.text)
            if response.status_code == 200:
                states = response_dict
                df = pd.DataFrame(states)
                df['payload_datestamp'] = df['payload_datestamp'].apply(lambda x: dtparse(x))
                df.set_index('payload_datestamp', inplace=True)
                df_list.append(df)
            elif response.status_code == 204:
                print('[x] No state data exists for Account "{}"'.format(account_uuid))
                df_list.append(None)
            elif response.status_code == 400:
                bad_request_params = response_dict['bad_request_params']
                for param_key in bad_request_params:
                    if param_key == 'private_key':
                        print('[x] Account "{}" does not exist'.format(account_uuid))
                    elif param_key in payload:
                        print('[x] Specified {} "{}" is not valid for Account "{}"'.format(param_key.replace('_', ' ').title(),
                                                                                           payload[param_key],
                                                                                           account_uuid))
                    else:
                        print('[x] {} is not valid for Account "{}"'.format(param_key.replace('_', ' ').title(),
                                                                            account_uuid))
                df_list.append(None)
            elif response.status_code == 500:
                print('[x] Account state(s) not retrieved due to server error')
                df_list.append(None)
    return df_list


def show_balance(*account_uuids,
                 delta_type=None,
                 start_date=None,
                 as_of_date=None,
                 max_count=None,
                 all_states=True,
                 order_by_earliest=None,
                 tz=None):
    config = Config()
    sawtooth_data_uri = config.settings['endpoints']['hydrosledger']['hydrostp']
    sawtooth_data_uri += 'hydrosledger_account/state/'

    df_list = list()
    for account_uuid in account_uuids:
        payload = dict(account_uuid=account_uuid,
                       delta_type=delta_type,
                       start_date=start_date,
                       as_of_date=as_of_date,
                       max_count=max_count,
                       all_states=all_states,
                       order_by_earliest=order_by_earliest,
                       tz=tz,
                       finx_key=config.settings['identity']['finx_key'])
        try:
            response = requests.get(sawtooth_data_uri, params=payload)
        except requests.exceptions.RequestException:
            response = None
            print('[x] No Account state(s) retrieved due to server inaccessibility')
        if response is not None:
            response_dict = json.loads(response.text)
            if response.status_code == 200:
                states = response_dict
                df = pd.DataFrame(states)
                df['payload_datestamp'] = df['payload_datestamp'].apply(lambda x: dtparse(x))
                df.set_index('payload_datestamp', inplace=True)
                df_list.append(df)
            elif response.status_code == 204:
                print('[x] No state data exists for Account "{}"'.format(account_uuid))
                df_list.append(None)
            elif response.status_code == 400:
                bad_request_params = response_dict['bad_request_params']
                for param_key in bad_request_params:
                    if param_key == 'private_key':
                        print('[x] Account "{}" does not exist'.format(account_uuid))
                    elif param_key in payload:
                        print('[x] Specified {} "{}" is not valid for Account "{}"'.format(param_key.replace('_', ' ').title(),
                                                                                           payload[param_key],
                                                                                           account_uuid))
                    else:
                        print('[x] {} is not valid for Account "{}"'.format(param_key.replace('_', ' ').title(),
                                                                            account_uuid))
                df_list.append(None)
            elif response.status_code == 500:
                print('[x] Account state(s) not retrieved due to server error')
                df_list.append(None)
    init_notebook_mode(connected=True)
    r = lambda: random.randint(0, 255)
    random_line_color = lambda: '#{}02X{}02X{}02X'.format(r(), r(), r())
    trace_data = list()

    for df in df_list:
        df.sort_index(inplace=True)
        str_account_uuid = str(df[-1:]['account_uuid'][0])
        payload_datestamps = [dtparse(str(x)) for x in df.index.values]
        trace = go.Scatter(x=payload_datestamps,
                           y=list(df['balance']),
                           name=str_account_uuid,
                           line=dict(color=random_line_color()),
                           mode='lines',
                           opacity=0.8)
        trace_data.append(trace)

    layout = dict(title="Account Balance",
                  yaxis=dict(title='Balance'))
    fig = dict(data=trace_data, layout=layout)
    iplot(fig,
          show_link=False,
          config=dict(displaylogo=False,
                      modeBarButtonsToRemove=['sendDataToCloud']))


def submit_journal_entry(account_uuid,
                         journal_entry_uuid=None,
                         transaction_uuid=None,
                         units=None,
                         unit_amount=None,
                         unit_price=None,
                         credit_amount=None,
                         debit_amount=None,
                         payload_datestamp=None,
                         tz=None,
                         dependencies=None,
                         nonce=None,
                         submit_batch=True):
    config = Config()
    sawtooth_data_uri = config.settings['endpoints']['hydrosledger']['hydrostp']
    sawtooth_data_uri += 'journal_entry/submit/'
    payload = dict(account_uuid=account_uuid,
                   journal_entry_uuid=journal_entry_uuid,
                   transaction_uuid=transaction_uuid,
                   units=units,
                   unit_amount=unit_amount,
                   unit_price=unit_price,
                   credit_amount=credit_amount,
                   debit_amount=debit_amount,
                   payload_datestamp=str(payload_datestamp),
                   tz=tz,
                   dependencies=dependencies,
                   nonce=nonce,
                   submit_batch=submit_batch,
                   finx_key=config.settings['identity']['finx_key'])
    try:
        response = requests.get(sawtooth_data_uri, params=payload)
    except requests.exceptions.RequestException:
        response = None
        print('[x] Journal Entry not accepted due to server inaccessibility')
    if response is not None:
        response_dict = json.loads(response.text)
        if response.ok:
            if submit_batch is True:
                journal_entry_data = json.loads(response.text)
                print('[✓] Journal Entry "{}" has been processed for Account "{}"'.format(journal_entry_data['journal_entry_uuid'],
                                                                                          journal_entry_data['account_uuid']))
            else:
                return response_dict
        elif response.status_code == 400:
            bad_request_params = response_dict['bad_request_params']
            for param_key in bad_request_params:
                if param_key == 'private_key':
                    print('[x] Account "{}" does not exist'.format(account_uuid))
                elif param_key in payload:
                    print('[x] Specified {} "{}" is not valid'.format(param_key.replace('_', ' ').title(),
                                                                      payload[param_key]))
                else:
                    print('[x] {} is not valid'.format(param_key.replace('_', ' ').title()))
        elif response.status_code == 409:
            print('[x] Journal Entry not processed due to transaction validation error')
        elif response.status_code == 500:
            print('[x] Journal Entry not processed due to server error')


def submit_transaction(side_a_debit_account_uuid,
                       side_a_debit_value,
                       side_a_credit_account_uuid,
                       side_a_credit_value,
                       side_b_debit_account_uuid,
                       side_b_debit_value,
                       side_b_credit_account_uuid,
                       side_b_credit_value,
                       side_a_debit_units=None,
                       side_a_debit_quantity=None,
                       side_a_debit_unit_price=None,
                       side_a_credit_units=None,
                       side_a_credit_quantity=None,
                       side_a_credit_unit_price=None,
                       side_b_debit_units=None,
                       side_b_debit_quantity=None,
                       side_b_debit_unit_price=None,
                       side_b_credit_units=None,
                       side_b_credit_quantity=None,
                       side_b_credit_unit_price=None,
                       payload_datestamp=None,
                       tz=None):
    config = Config()
    sawtooth_data_uri = config.settings['endpoints']['hydrosledger']['hydrostp']
    sawtooth_data_uri += 'journal_entry/submit/batch/'
    transaction_dict = dict(transaction_uuid=uuid4(),
                            side_a_debit_account_uuid=side_a_debit_account_uuid,
                            side_a_debit_value=side_a_debit_value,
                            side_a_credit_account_uuid=side_a_credit_account_uuid,
                            side_a_credit_value=side_a_credit_value,
                            side_b_debit_account_uuid=side_b_debit_account_uuid,
                            side_b_debit_value=side_b_debit_value,
                            side_b_credit_account_uuid=side_b_credit_account_uuid,
                            side_b_credit_value=side_b_credit_value,
                            side_a_debit_units=side_a_debit_units,
                            side_a_debit_quantity=side_a_debit_quantity,
                            side_a_debit_unit_price=side_a_debit_unit_price,
                            side_a_credit_units=side_a_credit_units,
                            side_a_credit_quantity=side_a_credit_quantity,
                            side_a_credit_unit_price=side_a_credit_unit_price,
                            side_b_debit_units=side_b_debit_units,
                            side_b_debit_quantity=side_b_debit_quantity,
                            side_b_debit_unit_price=side_b_debit_unit_price,
                            side_b_credit_units=side_b_credit_units,
                            side_b_credit_quantity=side_b_credit_quantity,
                            side_b_credit_unit_price=side_b_credit_unit_price,
                            payload_datestamp=payload_datestamp,
                            tz=tz)
    journal_entry_dict_list = list()
    for side in 'a', 'b':
        for action in 'debit', 'credit':
            account_uuid = transaction_dict['side_{}_{}_account_uuid'.format(side, action)]
            if account_uuid is not None:
                journal_entry_dict = dict(journal_entry_uuid=str(uuid4()),
                                          transaction_uuid=str(transaction_dict['transaction_uuid']),
                                          account_uuid=str(account_uuid),
                                          units=transaction_dict['side_{}_{}_units'.format(side, action)],
                                          unit_amount=transaction_dict['side_{}_{}_quantity'.format(side, action)],
                                          unit_price=transaction_dict['side_{}_{}_unit_price'.format(side, action)],
                                          payload_datestamp=str(payload_datestamp),
                                          tz=tz)
                if action == 'credit':
                    journal_entry_dict['credit_amount'] = eval('side_{}_credit_value'.format(side))
                    journal_entry_dict['debit_amount'] = 0
                else:
                    journal_entry_dict['credit_amount'] = 0
                    journal_entry_dict['debit_amount'] = eval('side_{}_debit_value'.format(side))
                journal_entry_dict_list.append(journal_entry_dict)
    payload = dict(batch_data=json.dumps(journal_entry_dict_list),
                   finx_key=config.settings['identity']['finx_key'])
    try:
        response = requests.get(sawtooth_data_uri, params=payload)
    except requests.exceptions.RequestException:
        response = None
        print('[x] Transaction not processed due to server inaccessibility')
    if response is not None:
        response_dict = json.loads(response.text)
        if response.ok:
            print('[✓] Transaction "{}" processed'.format(transaction_dict['transaction_uuid']))
            for journal_entry_dict in journal_entry_dict_list:
                account_uuid = journal_entry_dict['account_uuid']
                journal_entry_uuid = journal_entry_dict['journal_entry_uuid']
                print('\t[✓] Journal Entry "{}" has been processed for Account "{}"'.format(journal_entry_uuid,
                                                                                            account_uuid))
        elif response.status_code == 400:
            bad_request_params = response_dict['bad_request_params']
            for param_key in bad_request_params:
                if param_key == 'private_key':
                    print('[x] Specified account uuid(s) (one or more) are not valid')
                elif param_key in payload:
                    print('[x] Specified {} "{}" is not valid'.format(param_key.replace('_', ' ').title(),
                                                                      payload[param_key]))
                else:
                    print('[x] {} is not valid'.format(param_key.replace('_', ' ').title()))
        elif response.status_code == 409:
            print('[x] Transaction not processed due to transaction validation error')
        elif response.status_code == 500:
            print('[x] Transaction not processed due to server error')


def submit_one_sided_transaction(side_a_debit_account_uuid,
                                 side_a_debit_value,
                                 side_a_credit_account_uuid,
                                 side_a_credit_value,
                                 side_a_debit_units=None,
                                 side_a_debit_quantity=None,
                                 side_a_debit_unit_price=None,
                                 side_a_credit_units=None,
                                 side_a_credit_quantity=None,
                                 side_a_credit_unit_price=None,
                                 payload_datestamp=None,
                                 tz=None):
    submit_transaction(side_a_debit_account_uuid=side_a_debit_account_uuid,
                       side_a_debit_value=side_a_debit_value,
                       side_a_credit_account_uuid=side_a_credit_account_uuid,
                       side_a_credit_value=side_a_credit_value,
                       side_b_debit_account_uuid=None,
                       side_b_debit_value=None,
                       side_b_credit_account_uuid=None,
                       side_b_credit_value=None,
                       side_a_debit_units=side_a_debit_units,
                       side_a_debit_quantity=side_a_debit_quantity,
                       side_a_debit_unit_price=side_a_debit_unit_price,
                       side_a_credit_units=side_a_credit_units,
                       side_a_credit_quantity=side_a_credit_quantity,
                       side_a_credit_unit_price=side_a_credit_unit_price,
                       payload_datestamp=str(payload_datestamp),
                       tz=tz)


# Comment Explanation: ran into an issue of request strings being too long when five or more payloads were
#                      included in the same batch (there does not seem be a way to get around this issue)
#                      will undeprecate function once issue is resolved
def submit_action_batch(*account_action_payloads):
    config = Config()
    sawtooth_data_uri = config.settings['endpoints']['hydrosledger']['hydrostp']
    sawtooth_data_uri += 'hydrosledger_account/submit/batch/'
    batch_data = base64.b64encode(bz2.compress(json.dumps(account_action_payloads).encode()))
    payload = dict(batch_data=batch_data,
                   finx_key=config.settings['identity']['finx_key'])
    try:
        response = requests.get(sawtooth_data_uri, params=payload)
    except requests.exceptions.RequestException:
        response = None
        print('[x] Batch not accepted due to server inaccessibility')
    if response is not None:
        if response.ok:
            response_dict = json.loads(response.text)
            param_set_list_str = bz2.decompress(base64.b64decode(response_dict['batch_data'])).decode()
            param_set_list = json.loads(param_set_list_str)
            print('[✓] Batch processed')
            for param_set in param_set_list:
                action = param_set['action']
                account_uuid = param_set['account_uuid']
                if action in ('debit', 'credit'):
                    journal_entry_uuid = param_set['journal_entry_uuid']
                    print('\t[✓] Journal Entry "{}" has been processed for Account "{}"'.format(journal_entry_uuid,
                                                                                                account_uuid))
                if action == 'edit':
                    print('\t[✓] Account "{}" has been edited'.format(account_uuid))
        elif response.status_code == 400:
            response_dict = json.loads(response.text)
            bad_request_params = response_dict['bad_request_params']
            for param_key in bad_request_params:
                if param_key == 'private_key':
                    print('[x] Specified account uuid(s) (one or more) are not valid')
                elif param_key in payload:
                    print('[x] Specified {} "{}" is not valid'.format(param_key.replace('_', ' ').title(),
                                                                      payload[param_key]))
                else:
                    print('[x] {} is not valid'.format(param_key.replace('_', ' ').title()))
        elif response.status_code == 409:
            print('[x] Batch not processed due to transaction validation error')
        elif response.status_code == 414:
            print('[x] Too many payloads have been included in batch. '
                  'Please reduce number of payloads in batch and try again.')
        elif response.status_code == 500:
            print('[x] Batch not processed due to server error')


VALID_FUNCTION_CALLS = ['create_account',
                        'edit_account',
                        'get_account',
                        'get_accounts',
                        'show_balance',
                        'submit_journal_entry',
                        'submit_transaction',
                        'submit_one_sided_transaction',
                        'submit_action_batch']


def get_function_call_params(function_call=False, valid_function_calls=False):
    function_call_to_params_map = dict()
    for function_call_key in VALID_FUNCTION_CALLS:
        fun = inspect.getfullargspec(eval(function_call_key))
        params_list = list()
        if fun.args:
            no_default = 'no inspected default'
            fun_defaults = list(fun.defaults)
            fun_defaults = [no_default] * (len(fun.args) - len(fun.defaults)) + fun_defaults
            for param, default in zip(fun.args, fun_defaults):
                if default is not no_default:
                    param = '{} (default={})'.format(param, default)
                params_list.append(param)
            if fun.varargs:
              params_list.append('*' + fun.varargs)
            if fun.varkw:
              params_list.append('**' + fun.varkw)
        if fun.kwonlydefaults:
          params_list.append('*' + fun.varargs)
          parsed_kwonly = ['{} (defaults={})'.format(key, value)
                           for key, value in fun.kwonlydefaults.items()]
          params_list.extend(parsed_kwonly)
        if not fun.args and not fun.kwonlydefaults and fun.varargs:
            params_list.append('*' + fun.varargs)
        function_call_to_params_map[function_call_key] = params_list
    if bool(valid_function_calls):
        return list(function_call_to_params_map.keys())
    if bool(function_call):
        return function_call_to_params_map[function_call]


def help(*function_calls):
    valid_function_calls = get_function_call_params(valid_function_calls=True)
    if not function_calls:
        print("\033[1mValid function calls are\033[0m:\n\t\t\t• {}"
              .format("\n\t\t\t• ".join(valid_function_calls[:])))
        function_calls = valid_function_calls
    for function_call in function_calls:
        try:
            params = get_function_call_params(function_call)
            if isinstance(params, tuple) or isinstance(params, list):
                print("Parameters for \033[1m{}\033[0m:\n\t\t\t• {}"
                      .format(function_call, "\n\t\t\t• ".join(params[:])))
            else:
                print("Parameters for \033[1m{}\033[0m:\n\t\t\t• {}"
                      .format(function_call, params))
        except:
            print("\033[1mValid function calls are\033[0m:\n\t\t\t• {}"
                  .format("\n\t\t\t• ".join(valid_function_calls[:])))
            return "error: function {} does not exist".format(function_call)
