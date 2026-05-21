document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form[action^='/api/investigations/'][action$='/run']");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const response = await fetch(form.getAttribute("action"), { method: "POST" });
      if (response.ok) {
        window.location.reload();
      } else {
        const payload = await response.json();
        alert(payload.detail || "Failed to run investigation.");
      }
    });
  }
});
