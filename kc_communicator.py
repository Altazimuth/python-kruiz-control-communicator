#
# Kruiz Control WebSocket Communicator
# Copyright (c) 2024 Max Waine
# SPDX: GPL-2.0-or-later
#

import importlib
import pkgutil
import time
import inspect

from pathlib import Path

from plugin_interface import PluginInterface
import kc_obs
import plugins

ROOT_DIR = (Path(__file__).resolve().parent).resolve()

#
# Load all modules in the ./plugins folder
#
def load_plugins():
    plugin_instances = []
    for _, name, _ in pkgutil.iter_modules(plugins.__path__, plugins.__name__ + "."):
        module = importlib.import_module(name)
        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, PluginInterface) and obj != PluginInterface:
                plugin_instances.append(obj())
    return plugin_instances

#
# Wow. It's main. Wow.
#
if __name__ == '__main__':
    plugin_instances = load_plugins()
    kc_obs.init(plugin_instances)

    for plugin in plugin_instances:
        plugin.init()

    # Spin until the user does a keyboard interrupt (usually Ctrl+C)
    try:
        while True:
            time.sleep(1) # Pretty sure we could sleep forever but let's just sleep a second
    except KeyboardInterrupt:
        pass

    kc_obs.stop()
