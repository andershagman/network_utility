document.addEventListener("DOMContentLoaded", () => {
    console.log("switch.js loaded");

    const switchData = [
        {
            name: "kif-3505-l2-a sw1",
            groups: 4,
            ports: {
                "1": "connected",
                "2": "connected",
                "3": "notused",
                "5": "connected",
                "7": "notused",
                "9": "notused",
                "11": "notused",
                "13": "connected",
                "15": "notused",
                "17": "connected",
                "U1": "connected"
            }
        },
        {
            name: "kif-3505-l2-a sw2",
            groups: 4,
            ports: {
                "1": "connected",
                "2": "notused",
                "3": "connected",
                "48": "notconnected",
                "U1": "connected"
            }
        }
    ];

    const container = document.getElementById("container");

    function toggleMenu() {
        const dropdown = document.getElementById("dropdown");
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    }

    function createPort(label, status = "notconnected") {
        const port = document.createElement("div");
        port.className = `port ${status}`;
        port.innerText = label;
        return port;
    }

    function createPortGroup(start, count, portStatus) {
        const group = document.createElement("div");
        group.className = "port-group";

        const row1 = document.createElement("div");
        row1.className = "port-row";
        const row2 = document.createElement("div");
        row2.className = "port-row";

        console.log("PortStatus in group:", portStatus); // Debugging portStatus

        for (let i = 0; i < count; i++) {
            const portNumber = start + i;
            const label = portNumber.toString();
            const status = portStatus[label] || "notconnected";
            const port = createPort(label, status);

            if (portNumber % 2 === 1) {
                row1.appendChild(port);
            } else {
                row2.appendChild(port);
            }
        }

        group.appendChild(row1);
        group.appendChild(row2);
        return group;
    }

    function createUplinkGroup(uplinkStatus) {
        const group = document.createElement("div");
        group.className = "uplink-group";
    
        const row1 = document.createElement("div");
        row1.className = "port-row";
        const row2 = document.createElement("div");
        row2.className = "port-row";
    
        const ports = Object.entries(uplinkStatus)
            .filter(([label, _]) => label.startsWith("U"))
            .sort(([a], [b]) => parseInt(a.slice(1)) - parseInt(b.slice(1)));
    
        const portCount = ports.length;
    
        if (portCount === 8) {
            // Full 8-port uplinkmodul, 2 rader à 4 portar
            ports.forEach(([label, status], index) => {
                const port = createPort(label, status);
                if (index < 4) {
                    row1.appendChild(port);
                } else {
                    row2.appendChild(port);
                }
            });
            group.appendChild(row1);
            group.appendChild(row2);
        } else if (portCount === 4) {
            // 4-portars modul, centrera i höjdled (en rad)
            const spacer = document.createElement("div");
            spacer.className = "port-row empty-row";
            group.appendChild(spacer); // Top padding
    
            const middleRow = document.createElement("div");
            middleRow.className = "port-row";
            ports.forEach(([label, status]) => {
                const port = createPort(label, status);
                middleRow.appendChild(port);
            });
            group.appendChild(middleRow);
    
            const spacer2 = document.createElement("div");
            spacer2.className = "port-row empty-row";
            group.appendChild(spacer2); // Bottom padding
        } else {
            // Hantera övrigt antal (visa i övre raden bara)
            ports.forEach(([label, status]) => {
                const port = createPort(label, status);
                row1.appendChild(port);
            });
            group.appendChild(row1);
        }
    
        return group;
    }

    function createSwitch({ name, groups, ports }) {
        console.log("createSwitch received ports:", ports);

        const sw = document.createElement("div");
        sw.className = "switch";

        const title = document.createElement("div");
        title.className = "switch-title";
        title.textContent = name;

        const portContainer = document.createElement("div");
        portContainer.className = "port-container";

        // Debugging ports
        console.log("🔧 createSwitch() using ports:", ports);
        console.log("Ports keys:", Object.keys(ports));

        // Create port groups
        for (let i = 0; i < 4; i++) {
            if (i < groups) {
                const start = i * 12 + 1;
                const groupPorts = {};
                for (let j = 0; j < 12; j++) {
                    const portNum = (start + j).toString(); // e.g. "1"
                    if (ports && ports[portNum] !== undefined) {
                        groupPorts[portNum] = ports[portNum];
                    }
                }
                console.log("GroupPorts for group", i + 1, groupPorts);
                portContainer.appendChild(createPortGroup(start, 12, groupPorts));
            } else {
                const emptyGroup = document.createElement("div");
                emptyGroup.className = "port-group";
                portContainer.appendChild(emptyGroup);
            }
        }

        // Create uplinks
        const uplinkPorts = {};
        for (let i = 1; i <= 8; i++) {
            const label = "U" + i;
            if (ports && ports[label]) {
                uplinkPorts[label] = ports[label];
            }
        }
        portContainer.appendChild(createUplinkGroup(uplinkPorts));

        sw.appendChild(title);
        sw.appendChild(portContainer);
        container.appendChild(sw);
    }

    function renderSwitches(data) {
        console.log("renderSwitches received:", data);

        // Remove dummy switches
        document.querySelectorAll(".switch.dummy").forEach(el => el.remove());
        container.innerHTML = "";

        data.forEach(sw => {
            // Convert port_status_map to ports with string keys
            const ports = {};
            for (const [key, value] of Object.entries(sw.port_status_map || {})) {
                ports[String(key)] = value;
            }

            // Calculate number of groups
            const portKeys = Object.keys(ports).filter(k => !k.startsWith("U"));
            const groups = Math.ceil(portKeys.length / 12);

            createSwitch({
                name: sw.name,
                groups,
                ports
            });
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        const button = document.getElementById("fetchButton");
        if (button) {
            button.addEventListener("click", () => {
                renderSwitches(switchData);
            });
        }
    });

    // Expose functions globally
    window.renderSwitches = renderSwitches;
    window.createSwitch = createSwitch;
});
