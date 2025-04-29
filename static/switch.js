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

  for (let i = 0; i < count; i++) {
    const portNumber = start + i;
    const label = portNumber.toString();
    const status = portStatus[label] || "notconnected";
    const port = createPort(label, status);

    if (portNumber % 2 === 1) {
      row1.appendChild(port); // udda -> övre rad
    } else {
      row2.appendChild(port); // jämna -> nedre rad
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

  for (let i = 1; i <= 8; i++) {
    const label = "U" + i;
    const status = uplinkStatus[label] || "notconnected";
    const port = createPort(label, status);

    if (i % 2 === 1) {
      row1.appendChild(port); // udda -> övre rad
    } else {
      row2.appendChild(port); // jämna -> nedre rad
    }
  }

  group.appendChild(row1);
  group.appendChild(row2);
  return group;
}

    function createSwitch({ name, groups, ports }) {
      console.log("Creating switch: " + name);  // Lägg till denna rad
      const sw = document.createElement("div");
      sw.className = "switch";

      const title = document.createElement("div");
      title.className = "switch-title";
      title.textContent = name;

      const portContainer = document.createElement("div");
      portContainer.className = "port-container";

      for (let i = 0; i < 4; i++) {
        if (i < groups) {
          portContainer.appendChild(createPortGroup(i * 12 + 1, 12, ports));
        } else {
          const empty = document.createElement("div");
          empty.className = "port-group";
          portContainer.appendChild(empty);
        }
      }

      portContainer.appendChild(createUplinkGroup(ports));

      sw.appendChild(title);
      sw.appendChild(portContainer);
      container.appendChild(sw);
    }

switchData.forEach(sw => createSwitch(sw));

});
