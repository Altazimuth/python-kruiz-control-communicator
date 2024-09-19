#
# veadotube-mini WebSocket Communicator
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#

import os
import json
import sys

sys.path.append("..")
from kc_obs import send_kruiz_control_message

try:
    from websockets.sync.client import connect
except:
    print("You are missing websockets. To install run 'pip install websockets'")

class VeadoMiniInstance:
    def __init__(self, name: str, address: str):
        self.websocket = connect(f"ws://{address}?n=Deervourer")
        self.name      = name
        self.address   = address
        self.states    = self.get_states()

    #
    # Send stateEvents-type payload, with or without argument
    #
    def send_state_event_payload(self, event: str, arg_name: str = '', arg: str = ''):
        message = {
            'event': 'payload',
            'type': 'stateEvents',
            'id': 'mini',
            'payload': {
                'event': f'{event}'
            }
        }
        if arg_name and arg:
            message['payload'][arg_name] = arg

        self.websocket.send('nodes:' + json.dumps(message))
        return self.websocket.recv()

    #
    # For a websocket get all of the states available and put them into a name->id dict.
    #
    def get_states(self) -> dict[str, int]:
        states = {}

        recv_data   = self.send_state_event_payload('list')
        nodes       = recv_data[recv_data.find(':')+1:recv_data.rfind('}')+1]
        nodes_json  = json.loads(nodes)
        states_json = nodes_json["payload"]["states"]
        for state in states_json:
            states[state["name"]] = int(state["id"])

        return states

    #
    def change_state(self, change_type: str, name: str):
        self.send_state_event_payload(change_type, 'state', self.states[name])

    def set_state(self, name: str):
        self.send_state_event_payload('set', 'state', self.states[name])

    def push_state(self, name: str):
        self.send_state_event_payload('push', 'state', self.states[name])
    
    def pop_state(self, name: str):
        self.send_state_event_payload('pop', 'state', self.states[name])

VEADOMINI_LEN = len('veadotube mini - ')

instances = {}
active = True

#
# Kruiz Control event handler.
#
def handle_event(event_message: str, event_data: str) -> bool:
    if not active:
        return False

    if event_message == 'VeadoMini_SetState':
        change_state_method = VeadoMiniInstance.set_state
    elif event_message == 'VeadoMini_PushState':
        change_state_method = VeadoMiniInstance.push_state
    elif event_message == 'VeadoMini_PopState':
        change_state_method = VeadoMiniInstance.pop_state
    else:
        return False

    print(f"Received veadotube-mini event: {event_message}, {event_data}")
    [instance, state] = event_data.split(' ')

    target_instances = [instance] if instance != '*' else instances

    for instance in target_instances:
        change_state_method(target_instances[instance], state)

    return True

#
# Initialise. Wow.
#
def init():
    global active

    try:
        instance_dir = os.path.expanduser('~/.veadotube/instances')

        print("Initialising veadotube-mini WebSocket")
        for file in os.listdir(instance_dir):
            filename = os.fsdecode(file)

            try:
                instance_json = json.loads(open(instance_dir + '/' + filename, 'r').read())
            except json.JSONDecodeError:
                continue
            instance = VeadoMiniInstance(instance_json['name'][VEADOMINI_LEN:], instance_json['server'])
            instances[instance.name] = instance

        if instances:
            print("Available instance names:")
            for instance in instances:
                print(f" * {instance}")

        print("Successfully connected to veadotube-mini WebSocket")
    except:
        print("Failed to connect to veadotube-mini WebSocket")
        active = False
