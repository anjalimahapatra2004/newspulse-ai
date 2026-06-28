// Applied before paint as much as possible to avoid a flash of the wrong theme.
(function () {
  const stored = localStorage.getItem("newspulse_theme");
  if (stored === "dark") document.documentElement.setAttribute("data-theme", "dark");
})();

function toggleTheme() {
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  if (isDark) {
    document.documentElement.removeAttribute("data-theme");
    localStorage.setItem("newspulse_theme", "light");
  } else {
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("newspulse_theme", "dark");
  }
  const btn = document.querySelector(".theme-toggle");
  if (btn) btn.textContent = isDark ? "🌙" : "☀️";
}

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.createElement("button");
  btn.className = "theme-toggle";
  btn.setAttribute("aria-label", "Toggle dark mode");
  btn.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "☀️" : "🌙";
  btn.onclick = toggleTheme;
  document.body.appendChild(btn);
});