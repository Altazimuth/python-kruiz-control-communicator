#
# Kruiz Control WebSocket Communicator
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#

import sys
import os
import subprocess
import json
import re
from queue import Queue
from pathlib import Path
from threading import Lock

sys.path.append("..")
from plugin_interface import PluginInterface
from kc_obs import send_kruiz_control_message

WAV_DIR = './sam/wav'
SAM_EXE = './sam/sam.exe'

class SAMPlugin(PluginInterface):
    lock: Lock
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
            print("Received Subscription Message TTS:")
            print(f"\tUser: {user_name}")
            print(f"\tText: {text}")

            # TODO: Attach usernames to settings
            self.wav_queue.put(text)
        elif event_message == 'TTS_Play':
            if self.wav_queue.empty():
                return

            self.lock.acquire()

            text = self.wav_queue.get()
            self.next_wav += 1
            media_path = str((self.wav_path / f'sam{self.next_wav}.wav').absolute())
            subprocess.run([SAM_EXE, '-wav', media_path, text])

            self.lock.release()

            print(f"Playing TTS: sam{self.next_wav}.wav")
            send_kruiz_control_message("TTS_Ready", media_path)

    #
    # Initialise. Wow.
    #
    def init(self) -> bool:
        if os.path.exists(SAM_EXE):
            self.lock = Lock()
            self.wav_queue = Queue()

            self.wav_path = Path(WAV_DIR)
            self.wav_path.mkdir(exist_ok=True)

            p = re.compile(r'^sam(\d+)$')

            # TODO: Axe the current WAV naming schema and instead go with some sorta username-timedate thing
            # The problem with Python is it makes me want to do stuff like
            # self.next_wav = max([0] + [int(result.group(1)) for result in (p.search(file.stem) for file in self.wav_path.iterdir()) if result])
            # but I know that's ugly as sin.
            self.next_wav = 0
            for file in self.wav_path.iterdir():
                result = p.search(file.stem)
                if result:
                    self.next_wav = max(self.next_wav, int(result.group(1)))

            print('SAM found.')
            self.active = True
            return True
        else:
            print('SAM not found.')
            self.active = False
            return False
