# set all files in dir as importable
import os
import importlib
import logging
log = logging.getLogger(__name__)

for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    importlib.import_module(f".{module[:-3]}", package="importers")
    log.debug(f"Importer loaded: {module[:-3]}")