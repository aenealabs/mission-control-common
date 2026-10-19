// Mission Control shared behavior: theme toggle (Brightlayer Blue / Dark), phone menu, and the
// suite app menu. Loaded in <head> without defer so the saved theme applies before first paint.
(function () {
  const root = document.documentElement;

  function storedTheme() {
    try { return localStorage.getItem("bp-theme"); } catch { return null; }
  }
  function setTheme(theme) {
    root.dataset.theme = theme;
    try { localStorage.setItem("bp-theme", theme); } catch { /* storage unavailable */ }
    const icon = document.getElementById("theme-icon");
    if (icon) icon.textContent = theme === "dark" ? "light_mode" : "dark_mode";
  }

  const initial = storedTheme() ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  setTheme(initial);

  document.addEventListener("click", (event) => {
    if (event.target.closest("#theme-toggle")) {
      setTheme(root.dataset.theme === "dark" ? "light" : "dark");
    }
  });
  document.addEventListener("DOMContentLoaded", () => setTheme(root.dataset.theme));

  // Phone menu: open and close the side navigation.
  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    const button = document.getElementById("nav-toggle");
    if (button) button.setAttribute("aria-expanded", String(open));
  }
  document.addEventListener("click", (event) => {
    if (event.target.closest("#nav-toggle")) { setNav(!document.body.classList.contains("nav-open")); return; }
    if (document.body.classList.contains("nav-open") && !event.target.closest(".drawer")) setNav(false);
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") setNav(false); });

  // Suite app menu: close when clicking elsewhere or pressing Escape.
  document.addEventListener("click", (event) => {
    document.querySelectorAll("details.suite-menu[open]").forEach((menu) => {
      if (!menu.contains(event.target)) menu.open = false;
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") document.querySelectorAll("details.suite-menu[open]").forEach((m) => { m.open = false; });
  });
})();
