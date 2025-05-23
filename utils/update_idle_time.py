import subprocess
import re
import pymongo

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "network"
COLLECTION = "switches"

OID_IFDESCR = "IF-MIB::ifDescr"
OID_IFOPERSTATUS = "IF-MIB::ifOperStatus"
OID_IFLASTCHANGE = "IF-MIB::ifLastChange"
OID_SYSUPTIME = "DISMAN-EVENT-MIB::sysUpTimeInstance"

def snmp_walk(ip, oid):
    try:
        result = subprocess.check_output(["snmpwalk", "-v2c", "-c", "public", ip, oid], timeout=5)
        return result.decode().strip().split("\n")
    except Exception as e:
        print(f"SNMP error on {ip}: {e}")
        return []

def get_sys_uptime(ip):
    try:
        result = subprocess.check_output(["snmpget", "-v2c", "-c", "public", ip, OID_SYSUPTIME], timeout=5)
        match = re.search(r'\((\d+)\)', result.decode())
        return int(match.group(1)) if match else 0
    except Exception as e:
        print(f"Failed to get sysUpTime from {ip}: {e}")
        return 0

def extract_ifindex(line):
    match = re.search(r"\.(\d+)\s*=", line)
    return int(match.group(1)) if match else None

def extract_lastchange_ticks(line):
    match = re.search(r"\((\d+)\)", line)
    return int(match.group(1)) if match else 0

def extract_value(line):
    return line.split(":")[-1].strip()

def extract_operstatus_value(line):
    match = re.search(r":\s*\w+\((\d+)\)", line)
    return int(match.group(1)) if match else 2  # fallback = down

def update_idle_times(ip, name):
    print(f"Startar uppdatering för {name} ({ip})")

    descrs = snmp_walk(ip, OID_IFDESCR)
    statuses = snmp_walk(ip, OID_IFOPERSTATUS)
    lastchanges = snmp_walk(ip, OID_IFLASTCHANGE)
    current_uptime = get_sys_uptime(ip)

    print(f"{name}: {len(statuses)} ifOperStatus-poster")
    print(f"{name}: {len(lastchanges)} ifLastChange-poster")

    if not (descrs and statuses and lastchanges and current_uptime):
        error_msg = f"{name}: SNMP timeout or missing data."
        print(error_msg)
        raise RuntimeError(error_msg)

    port_data = {}
    for line in descrs:
        idx = extract_ifindex(line)
        if idx is not None:
            port_data[idx] = {"name": extract_value(line)}

    for line in statuses:
        idx = extract_ifindex(line)
        if idx in port_data:
            val = extract_operstatus_value(line)
            port_data[idx]["status"] = "up" if val == 1 else "down"

    for line in lastchanges:
        idx = extract_ifindex(line)
        if idx in port_data:
            port_data[idx]["lastchange"] = extract_lastchange_ticks(line)

    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION]
    doc = col.find_one({"name": name})
 
    print(f"Hämtade dokument för {name}: {doc}")

    old_ports = {p["name"]: p for p in doc.get("ports", [])}
    last_uptime = doc.get("switch_uptime", 0)

    updated_ports = []
    used = 0
    for idx, pdata in port_data.items():
        portname = pdata["name"]
        status = pdata.get("status", "down")
        lastchange = pdata.get("lastchange", 0)

        previous = old_ports.get(portname, {})
        old_idle = previous.get("idle_time", 0)

        if status == "down" and (current_uptime - lastchange) >= (current_uptime - last_uptime):
            # Port har varit nere hela tiden
            idle_time = old_idle + (current_uptime - last_uptime) / 100.0
        else:
            # Port kan ha varit nere eller uppe delvis
            idle_time = (current_uptime - lastchange) / 100.0 if status == "down" else 0

        if status == "up":
            used += 1

        updated_ports.append({
            "name": portname,
            "status": status,
            "idle_time": round(idle_time, 1)
        })

    total = len(updated_ports)

    # Efter att updated_ports har byggts
    port_status_map = {}
    
    for p in updated_ports:
        pname = p["name"]
        status = p["status"]
        idle = p["idle_time"]
    
        # Standardvärde
        state = "connected" if status == "up" else "notconnected"
        if status != "up" and idle == 0:
            old_idle = old_ports.get(pname, {}).get("idle_time", None)
            state = "notused" if old_idle is None else "notconnected"
    
        # Extrahera stack-nummer och portnummer
        match = re.match(r".*?(\d+)/(\d+)/(\d+)", pname)
        if match:
            stack_num, module_num, port_num = match.groups()
            shortname = f"U{port_num}" if module_num != "0" else port_num
            if stack_num not in port_status_map:
                port_status_map[stack_num] = {}
            port_status_map[stack_num][shortname] = state
        else:
            # Fallback om formatet inte matchar
            port_status_map.setdefault("1", {})[pname] = state
            
        free = total - used
        used_percent = round(100 * used / total, 1) if total else 0
    
    col.update_one(
        {"name": name},
        {"$set": {
            "ports": updated_ports,
            "port_status_map": port_status_map,  # <--- Lägg till denna
            "used": used,
            "free": free,
            "used_percent": used_percent,
            "switch_uptime": current_uptime
        }}
    )
    print(f"{name}: updated {total} ports")

# Exempel: hämta från alla switches i databasen
if __name__ == "__main__":
    client = pymongo.MongoClient(MONGO_URI)
    col = client[DB_NAME][COLLECTION]
    for switch in col.find():
        if "name" in switch and "ip" in switch:
            print(f"Skriver {len(updated_ports)} portar till databasen.")
            update_idle_times(switch["ip"], switch["name"])
