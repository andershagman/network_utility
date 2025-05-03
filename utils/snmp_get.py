import subprocess
import json

def run_snmpwalk(ip, community, oid):
    try:
        result = subprocess.run(
            ["snmpwalk", "-v2c", "-r", "2", "-c", community, ip, oid],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.splitlines()
    except Exception as e:
        print(f"SNMP error: {e}")
        return []

def parse_snmp_dict(lines, expected_key):
    data = {}
    for line in lines:
        if expected_key in line:
            parts = line.split("::")[1].split(" = ")
            index = parts[0].split(".")[1]
            value = parts[1].split(":")[1].strip()
            data[index] = value
    return data

import json

def safe_error_message(message):
    return message.encode('utf-8').decode('utf-8')

def get_ports_data(ip, community="public"):
    try:
        # Hämta SNMP-data
        descr_lines = run_snmpwalk(ip, community, "IF-MIB::ifDescr")
        status_lines = run_snmpwalk(ip, community, "IF-MIB::ifOperStatus")
        lastchange_lines = run_snmpwalk(ip, community, "IF-MIB::ifLastChange")

        # Kontrollera om någon av walk-kommandoerna returnerar felaktig data (t.ex. timeout)
        if not descr_lines or not status_lines or not lastchange_lines:
            error_message = f"Timeout eller ingen data från switchen med IP: {ip}"
            return {
                "error": safe_error_message(error_message)
            }

        # Bearbeta SNMP-data till dictionaries
        descr = parse_snmp_dict(descr_lines, "ifDescr")
        status = parse_snmp_dict(status_lines, "ifOperStatus")
        lastchange = parse_snmp_dict(lastchange_lines, "ifLastChange")

        # Lista för att lagra portdata
        ports = []
        used = 0
        free = 0

        # Bygg portdata och räkna användna och lediga portar
        for index in descr.keys():
            port_status = status.get(index, "unknown")

            # Räkna användna och lediga portar baserat på status
            if port_status == "up(1)":  # Port är up (aktiv)
                used += 1
            else:
                free += 1

            ports.append({
                "index": index,
                "name": descr.get(index, "N/A"),
                "status": port_status,
                "last_change": lastchange.get(index, "N/A")
            })

        # Beräkna procentandel av använda portar
        total_ports = used + free
        used_percent = round(used / total_ports * 100) if total_ports > 0 else 0  # Hantera delning med 0

        # Returnera data om portar samt statistiken
        return {
            "ports": ports,
            "used": used,
            "free": free,
            "used_percent": used_percent
        }

    except Exception as e:
        # Om något annat fel inträffar (t.ex. nätverksfel)
        error_message = f"Något gick fel vid anslutning till switchen: {e}"
        return {
            "error": safe_error_message(error_message)
        }

# Exempelanrop
if __name__ == "__main__":
    ip = "10.211.55.9:1161"  # byt till din switch
    community = "public"
    ports = get_ports_data(ip, community)
    print(json.dumps(ports, indent=2))
