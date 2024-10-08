#
# SAMMI Webhook Sender
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#
# SAMMI doesn't have any native ways to talk back to this, so it'll have to do so by means of
# "Send OBS Command" and letting OBS then forward that on. An example of the JSON to send from SAMMI:
# {
#   "d": {
#     "requestData": {
#       "eventData": {
#         "data": {
#           "message": "MessageForKC",
#           "data": "SomeData"
#         },
#         "realm": "kruiz-control"
#       }
#     },
#     "requestType": "BroadcastCustomEvent"
#   },
#   "op": 6
# }
#
# In Kruiz Control you'd have something like:
# OnOBSCustomMessage "MessageForKC"
# Chat Send "Message: {message}. Data: {data}"
#

#from typing import Any

import sys

sys.path.append("..")
from plugin_interface import PluginInterface
from kc_obs import send_kruiz_control_message

try:
    import requests
except:
    print("You are missing requests. To install run 'pip install requests'")

#
# Send a message with a specific trigger and data to SAMMI.
#
def send_message(trigger: str, data: str): #data: dict[str, Any]):
    message = { 'trigger': trigger, 'customData': data }
    # We need to lower the timeout to send requests quickly
    requests.post(f'http://{sammi_url}', json=message, timeout=0.05)

sammi_url = 'localhost:9450/webhook'

class SAMMIPlugin(PluginInterface):
    @property
    def name() -> str:
        return "SAMMI"

    #
    # Kruiz Control event handler.
    #
    def handle_event(self, event_message: str, event_data: str) -> bool:
        if not self.active or event_message != 'SAMMI_SendMessage':
            return False

        print(f"Received SAMMI event")
        [trigger, data] = event_data.split(' ', 1)

        send_message(trigger, data)

        return True

    #
    # Initialise. Wow.
    #
    def init(self) -> bool:
        try:
            print("Searching for SAMMI webhook")
            requests.get(f'http://{sammi_url}')
            print("Found SAMMI webhook")
            return True
        except:
            print("Failed to find SAMMI webhook")
            self.active = False
            return False
