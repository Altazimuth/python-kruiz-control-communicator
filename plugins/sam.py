#
# Kruiz Control WebSocket Communicator
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#

import sys
import os
import subprocess

sys.path.append("..")
from kc_obs import send_kruiz_control_message

SAM_PATH = './sam/sam.exe'
active = True

#
# Kruiz Control event handler.
#
def handle_event(event_message: str, event_data: str) -> bool:
    if not active or event_message != 'TTS':
        return

    print(f"Received TTS Text:\n\t{event_data}")

    event_data = event_data.replace('"', '\\"') # DO NOT LET END-USERS BREAK OUT OF THEIR STRING LITERAL PRISON.

    subprocess.run(f'{SAM_PATH} "{event_data}"')

#
# Initialise. Wow.
#
def init():
    global active
    
    if os.path.exists(SAM_PATH):
        print('SAM found.')
        active = True
    else:
        print('SAM not found.')
        active = False
