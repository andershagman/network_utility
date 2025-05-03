# utils/inventory_sync.py

import requests
import logging
from pymongo import MongoClient
from utils.config import NETBOX_API, NETBOX_TOKEN

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Inställningar
ROLE_NAMES = ["L2-Switch", "L3-Switch"]
DB_NAME = "network"
COLLECTION_NAME = "switches"

# MongoDB
client = MongoClient()
db = client[DB_NAME]
inventory_col = db[COLLECTION_NAME]

# NetBox headers
headers = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Accept": "application/json",
}

def get_role_ids():
    url = f"{NETBOX_API}/api/dcim/device-roles/"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    all_roles = response.json()["results"]
    role_map = {r["name"]: r["id"] for r in all_roles}
    return [role_map[name] for name in ROLE_NAMES if name in role_map]

def get_netbox_devices():
    role_ids = get_role_ids()
    devices = []
    for role_id in role_ids:
        params = {
            "role_id": role_id,
            "has_primary_ip": "true",
            "status": "active"
        }
        url = f"{NETBOX_API}/api/dcim/devices/"
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        devices.extend(resp.json()["results"])

    result = []
    for dev in devices:
        ip = dev.get("primary_ip4", {}).get("address", "").split("/")[0]
        if not ip:
            continue
        result.append({
            "name": dev["name"],
            "ip": ip,
            "site": dev.get("site", {}).get("name", ""),
            "role": dev.get("role", {}).get("name", "")
        })
    return result

def sync_inventory():
    netbox_devices = get_netbox_devices()
    db_devices = {dev["name"]: dev for dev in inventory_col.find({}, {"_id": 0})}
    netbox_names = set()

    for dev in netbox_devices:
        name = dev["name"]
        netbox_names.add(name)

        if name not in db_devices:
            logger.info(f"[ADD] {name} ({dev['ip']})")
            inventory_col.insert_one(dev)
        else:
            changed = any(dev[k] != db_devices[name].get(k) for k in dev)
            if changed:
                logger.info(f"[UPDATE] {name} ({dev['ip']})")
                inventory_col.update_one({"name": name}, {"$set": dev})

    for name in db_devices:
        if name not in netbox_names:
            logger.info(f"[REMOVE] {name}")
            inventory_col.delete_one({"name": name})

    logger.info(f"Synkronisering klar. {len(netbox_devices)} enheter synkade.")

if __name__ == "__main__":
    sync_inventory()
