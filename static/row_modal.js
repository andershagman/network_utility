document.addEventListener("DOMContentLoaded", () => {
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

      // Fyll i rowModal
      document.getElementById("rowModalTitle").innerText = "Redigera post";
      document.getElementById("rowModalBody").innerHTML = html;

      // Visa modalen
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

  // Inuti klickhanteraren efter modalen visats
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

});

// row_modal.js

let currentDataType = "";

function openEmptyModal(type) {
  currentDataType = type;

  // Förifylld mall beroende på typ
  const templates = {
    users: {
      username: "",
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

  const rowData = templates[type];

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

  document.getElementById("rowModalTitle").innerText = `Ny ${type.slice(0, -1)}`;
  document.getElementById("rowModalBody").innerHTML = html;
  document.getElementById("rowModal").style.display = "block";
}

// Eventlyssnare för knappen Lägg till
["users", "groups", "permissions"].forEach((type) => {
  const btn = document.getElementById(`${type}AddBtn`);
  if (btn) {
    btn.addEventListener("click", () => openEmptyModal(type));
  }
});

