document.addEventListener("DOMContentLoaded", () => {
  // Lyssnar på klick på tabellen för att redigera en post
  const table = document.getElementById("dataTable");
  if (table) {
    table.addEventListener("click", (e) => {
      const row = e.target.closest("tr");
      if (!row || !row.dataset.row) return;

      const rowData = JSON.parse(row.dataset.row);

      // Bygg formulärinnehåll
      let html = '<form id="editForm">';
      for (const key in rowData) {
        html += `
          <label for="${key}">${key}</label>
          <input id="${key}" name="${key}" value="${rowData[key]}" /><br>
        `;
      }
      html += '</form>';

      // Fyll i modal med formulärinnehåll
      document.getElementById("rowModalTitle").innerText = "Redigera post";
      document.getElementById("rowModalBody").innerHTML = html;

      const deleteBtn = document.getElementById("rowDeleteBtn");
      if (deleteBtn) deleteBtn.style.display = "inline-block";
      // Visa modal
      const modal = document.getElementById("rowModal");
      if (modal) modal.style.display = "block";
    });
  }

  // Stäng modal när man klickar på Avbryt
  const cancelBtn = document.getElementById("rowCancelBtn");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      const modal = document.getElementById("rowModal");
      if (modal) modal.style.display = "none";
    });
  }

  // Hantera radering av posten
  const deleteBtn = document.getElementById("rowDeleteBtn");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", function (e) {
      const btn = e.target;

      if (!btn.dataset.confirmed) {
        btn.textContent = "Säkert?";
        btn.dataset.confirmed = "true";

        // Återställ efter 3 sekunder
        setTimeout(() => {
          btn.textContent = "Radera";
          delete btn.dataset.confirmed;
        }, 3000);
      } else {
        console.log("Raderar posten...");
        document.getElementById("rowModal").style.display = "none";
      }
    });
  }

  // Lägg till ny post (för användare, grupper, behörigheter)
  function openAddModal(type) {
    let rowData;
    const templates = {
      users: {
        username: "",
        password: "",
        email: "",
        role: "user",
        active: true,
      },
      groups: {
        name: "",
        description: "",
        members: [],
      },
      permissions: {
        name: "",
        description: "",
        level: 0,
      },
    };

    // Hämta mall beroende på typ
    rowData = templates[type];

    // Bygg formulärinnehåll för att lägga till ny post
    let html = '<form id="editForm">';
    for (const key in rowData) {
      let value = rowData[key];
      if (Array.isArray(value)) {
        html += `<label for="${key}">${key}</label><input id="${key}" name="${key}" value="" placeholder="kommaseparerad lista" /><br>`;
      } else if (typeof value === "boolean") {
        html += `<label for="${key}">${key}</label><input type="checkbox" id="${key}" name="${key}" ${value ? "checked" : ""} /><br>`;
      } else {
        html += `<label for="${key}">${key}</label><input id="${key}" name="${key}" value="${value}" /><br>`;
      }
    }
    html += '</form>';

    // Fyll i modal med ny postdata
    document.getElementById("rowModalTitle").innerText = `Ny ${type.slice(0, -1)}`;
    document.getElementById("rowModalBody").innerHTML = html;

    // Dölj delete-knappen vid ny post
    const deleteBtn = document.getElementById("rowDeleteBtn");
    if (deleteBtn) deleteBtn.style.display = "none";

    // Visa modal
    const modal = document.getElementById("rowModal");
    if (modal) modal.style.display = "block";
  }

  // Lägg till eventlyssnare för knappar för att lägga till nya poster
  ["users", "groups", "permissions"].forEach((type) => {
    const btn = document.getElementById(`${type}AddBtn`);
    if (btn) {
      btn.addEventListener("click", () => openAddModal(type));
    }
  });
  const addItemBtn = document.getElementById("addItemBtn");
  if (addItemBtn) {
    addItemBtn.addEventListener("click", () => {
      const path = window.location.pathname;

      let type = "";
      if (path.includes("/users")) {
        type = "users";
      } else if (path.includes("/groups")) {
        type = "groups";
      } else if (path.includes("/permissions")) {
        type = "permissions";
      } else {
        console.error("Okänd sida – ingen typ kunde bestämmas.");
        return;
      }

      openAddModal(type);
    });
  }
});
