#
# Kruiz Control WebSocket Communicator
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#

import sys
import os

from typing import Any, List

try:
    from obswebsocket import obsws, exceptions, requests, events
except:
    print("You are missing obs-websocket-py. To install run 'pip install obs-websocket-py'")
    sys.exit(1)

ws = obsws()
modules = []

from plugin_interface import PluginInterface

#
# This function exists because obswebsocket expects a response,
# which is something we're not going to get for a custom event.
# To work around this we temporarily set the timeout to basically nothing,
# call with the BroadcastCustomEvent request, catch the timeout exception,
# and reset timeout.
#
def send_custom_event(data: dict[str, Any]):
    timeout = ws.timeout
    ws.timeout = 0.001
    try:
        ws.call(requests.BroadcastCustomEvent(eventData=data))
    except:
        pass
    ws.timeout = timeout

#
# Sends a message to Kruiz Control for consumption with OnOBSCustomMessage <message>.
#
def send_kruiz_control_message(message: str, data: str):
    send_custom_event({'data': {'message': message, 'data': data}, 'realm': 'kruiz-control'})

#
# Handle an event with the 'kruiz-control' realm.
#
def on_kruiz_control_event(message):
    event_message = message.getData()['message']
    event_data    = message.getData()['data']

    # handle_event returns true is the event is eaten. We rely on short-circuiting here.
    any(module.handle_event(event_message, event_data) for module in modules)

#
# This is our hook for handling 'CustomEvent's, emitted by BroadcastCustomEvent.
# If you want to handle any other custom events, you probably need to handle a new realm.
#
def on_custom_event(message):
    if message.getRealm() == 'kruiz-control':
        on_kruiz_control_event(message)

def init(plugins: List[PluginInterface]):
    global modules, ws

    modules = plugins

    OBS_SETTING_PATHS = ('./obs/host.txt', './obs/port.txt', './obs/password.txt')

    if all(os.path.exists(path) for path in OBS_SETTING_PATHS):
        host     = open('./obs/host.txt', 'r').read().strip()
        port     = int(open('./obs/port.txt', 'r').read().strip())
        password = open('./obs/password.txt', 'r').read().strip()
    else:
        if not os.path.exists('./obs'): os.makedirs('./obs')
        for path in OBS_SETTING_PATHS:
            open(path, 'w').close()
        print("Please input your OBS settings into ./obs/host.txt, ./obs/port.txt, and ./obs/password.txt")
        sys.exit(0)

    # Try create the websocket.
    print("Initialising OBS websocket")
    ws = obsws(host, port, password, timeout=5)
    ws.register(on_custom_event, events.CustomEvent)
    try:
        ws.connect()
    except exceptions.ConnectionFailure as e:
        print(f"Failed to connect to OBS websocket: {e}")
        sys.exit(1)
    print("Successfully connected to OBS websocket")

def stop():
    ws.disconnect()
