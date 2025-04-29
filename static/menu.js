// Hamburgermeny
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("menuToggle");
  const content = document.getElementById("menuContent");

  if (toggle && content) {
    toggle.addEventListener("click", () => {
      content.classList.toggle("show");
    });
  }

  // Visa modalen
  const settingsBtn = document.getElementById("settings");
  if (settingsBtn) {
    settingsBtn.addEventListener("click", () => {
      const modal = document.getElementById("settingsModal");
      if (modal) modal.style.display = "block";
    });
  }

  // Göm modalen när OK klickas
  const okBtn = document.getElementById("settingsOkBtn");
  if (okBtn) {
    okBtn.addEventListener("click", () => {
      const data = {
        field1: document.getElementById("exampleField")?.value || "",
        field2: document.getElementById("extraField1")?.value || "",
        field3: document.getElementById("extraField2")?.value || "",
        val: document.querySelector('input[name="mode"]:checked')?.value || ""
      };

      fetch("/save-settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      }).then((response) => {
        if (response.ok) {
          console.log("Inställningar sparade");
          const modal = document.getElementById("settingsModal");
          if (modal) modal.style.display = "none";
        } else {
          console.error("Fel vid sparning");
        }
      });
    });
  }

  // Klick utanför modalen stänger den
  window.addEventListener("click", (e) => {
    const modal = document.getElementById("settingsModal");
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});
