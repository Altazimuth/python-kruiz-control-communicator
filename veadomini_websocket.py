#
# veadotube-mini WebSocket Communicator
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#

import os
import json

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

def init():
    instance_dir = os.path.expanduser('~/.veadotube/instances')

    print("Initialising veadotube-mini WebSocket")
    print("Available instance names:")
    for file in os.listdir(instance_dir):
        filename = os.fsdecode(file)

        instance_json = json.loads(open(instance_dir + '/' + filename, 'r').read())
        instance = VeadoMiniInstance(instance_json['name'][VEADOMINI_LEN:], instance_json['server'])
        print(f" * {instance.name}")
        instances[instance.name] = instance

    print("Successfully connected to veadotube-mini WebSocket")