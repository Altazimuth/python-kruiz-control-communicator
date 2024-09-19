#
# Kruiz Control WebSocket Communicator
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#

import importlib
import pkgutil
import time

import kc_obs
import plugins

#
# Load all modules in the ./plugins folder
#
def load_plugins():
    for _, name, _ in pkgutil.iter_modules(plugins.__path__, plugins.__name__ + "."):
        modules.append(importlib.import_module(name))

#
# Wow. It's main. Wow.
#
if __name__ == '__main__':
    modules = []

    load_plugins()
    kc_obs.init(modules)

    for module in modules:
        module.init()

    # Spin until the user does a keyboard interrupt (usually Ctrl+C)
    try:
        while True:
            time.sleep(1) # Pretty sure we could sleep forever but let's just sleep a second
    except KeyboardInterrupt:
        pass

    kc_obs.stop()
