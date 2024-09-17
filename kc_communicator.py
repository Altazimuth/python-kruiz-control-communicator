#
# Kruiz Control WebSocket Communicator
# Copyright (c) 2024 Max Waine
#
# This software is distributed under the terms of the Free Software Foundation's
# GNU GPLv2+. The full text can be found in LICENSE, which should be included with this
# program, or at https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html#SEC1.
#

import sys
import os
import time
import subprocess
from typing import Any

import veadomini_websocket

try:
    from obswebsocket import obsws, exceptions, requests, events
except:
    print("You are missing obs-websocket-py. To install run 'pip install obs-websocket-py'")
    sys.exit(1)

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

    if event_message == 'TTS':
        print(f"Received TTS Text:\n\t{event_data}")

        event_data = event_data.replace('"', '\\"') # DO NOT LET END-USERS BREAK OUT OF THEIR STRING LITERAL PRISON.

        subprocess.run(f'./sam.exe "{event_data}"')
        send_kruiz_control_message('DoneWithSAM', 'SomeFeedbackData')
    elif have_veadomini:
        print("Received")
        [instance, state] = event_data.split(' ')

        instances = [instance] if instance != '*' else veadomini_websocket.instances

        if event_message == 'VeadoMini_SetState':
            change_state_method = veadomini_websocket.VeadoMiniInstance.set_state
        elif event_message == 'VeadoMini_PushState':
            change_state_method = veadomini_websocket.VeadoMiniInstance.push_state
        elif event_message == 'VeadoMini_PopState':
            change_state_method = veadomini_websocket.VeadoMiniInstance.pop_state
        else:
            return

        for instance in instances:
            change_state_method(veadomini_websocket.instances[instance], state)

#
# This is our hook for handling 'CustomEvent's, emitted by BroadcastCustomEvent.
# If you want to handle any other custom events, you probably need to handle a new realm.
#
def on_custom_event(message):
    print(message)
    if message.getRealm() == 'kruiz-control':
        on_kruiz_control_event(message)

#
# Wow. It's main. Wow.
#
if __name__ == '__main__':
    OBS_SETTING_PATHS = ('./obs/host.txt', './obs/port.txt', './obs/password.txt')

    if all([os.path.exists(path) for path in OBS_SETTING_PATHS]):
        host     = open('./obs/host.txt', 'r').read().strip()
        port     = int(open('./obs/port.txt', 'r').read().strip())
        password = open('./obs/password.txt', 'r').read().strip()
    else:
        if not os.path.exists('./obs'): os.makedirs('./obs')
        for path in OBS_SETTING_PATHS:
            open(path, 'w').close()
        print("Please input your OBS settings into ./obs/host.txt, ./obs/port.txt, and ./obs/password.txt")
        sys.exit(0)


    have_veadomini = True
    try:
        veadomini_websocket.init()
    except:
        have_veadomini = False

    # Try create the websocket.
    print("Initialising OBS websocket")
    ws = obsws(host, port, password, timeout=5)
    ws.register(on_custom_event, events.CustomEvent)
    try:
        ws.connect()
    except exceptions.ConnectionFailure as e:
        print("Failed to connect to OBS websocket: {}".format(e))
        sys.exit(1)
    print("Successfully connected to OBS websocket")

    # Spin until the user does a keyboard interrupt (usually Ctrl+C)
    try:
        while True:
            time.sleep(1) # Pretty sure we could sleep forever but let's just sleep a second
    except KeyboardInterrupt:
        pass

    ws.disconnect()