#
# Kruiz Control WebSocket Communicator
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#

# This plugin relies on SAM. You can find it at:
# https://simulationcorner.net/index.php?page=sam

import sys
import os
import subprocess
import json
from datetime import datetime
from queue import Queue
from pathlib import Path

sys.path.append("..")
from plugin_interface import PluginInterface
from kc_obs import send_kruiz_control_message
from kc_communicator import ROOT_DIR

WAV_DIR = ROOT_DIR / 'sam/wav'
SAM_EXE = ROOT_DIR / 'sam/sam.exe'

class SAMPlugin(PluginInterface):
    wav_path: Path
    next_wav: int
    wav_queue: Queue

    @property
    def name() -> str:
        return "SAM"

    #
    # Kruiz Control event handler.
    #
    def handle_event(self, event_message: str, event_data: str) -> bool:
        if not self.active:
            return

        if event_message == 'TTS_Queue':
            data_json = json.loads(event_data)

            user_name: str = data_json['user_name']
            text: str = data_json['message']['text']
            time_str: str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            print("Received Subscription Message TTS:")
            print(f"\tUser: {user_name}")
            print(f"\tText: {text}")
            print(f"\tTime: {time_str}")

            self.wav_queue.put((user_name, text, time_str))
        elif event_message == 'TTS_Play':
            if self.wav_queue.empty():
                return

            user_name, text, time_str = self.wav_queue.get()
            filename: str = f'sam-{time_str}-{user_name}.wav'
            media_path: str = str((self.wav_path / filename))
            subprocess.run([SAM_EXE, '-wav', media_path, text])

            print(f"Playing TTS: {filename}")
            send_kruiz_control_message("TTS_Ready", media_path)

    #
    # Initialise. Wow.
    #
    def init(self) -> bool:
        if os.path.exists(SAM_EXE):
            self.wav_queue = Queue()

            self.wav_path = Path(WAV_DIR)
            self.wav_path.mkdir(exist_ok=True)

            print('SAM found.')
            self.active = True
            return True
        else:
            print('SAM not found.')
            self.active = False
            return False
