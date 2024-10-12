import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
cogs=[]
loaded_cogs = []
all_cogs=[]
def load_cogs():
    global cogs, loaded_cogs, all_cogs
    try:
        cogs = json.load(open("./cogs/cogs.json"))
    except FileNotFoundError:
        logger.error("cogs.json not found... please see if the file exists in the cogs directory.")
        cogs = []
    except json.JSONDecodeError:
        logger.error("cogs.json is not a valid json file...")
        cogs = []

    for cog in cogs:
        if cog['is_enabled']:
            loaded_cogs.append(cog['name'])
        all_cogs.append(cog['name'])
load_cogs()
def update_cogs(loaded):
    global cogs
    for cog in cogs:
        if cog['name'] in loaded:
            cog['is_enabled'] = True
        else:
            cog['is_enabled'] = False
    with open("./cogs/cogs.json", "w") as f:
        json.dump(cogs, f, indent=4)