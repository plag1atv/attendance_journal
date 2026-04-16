const root = document.documentElement;
const themeToggle = document.getElementById("themeToggle");

const savedTheme = localStorage.getItem("site-theme");
if (savedTheme) {
    root.setAttribute("data-theme", savedTheme);
}

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const currentTheme = root.getAttribute("data-theme") || "light";
        const nextTheme = currentTheme === "light" ? "dark" : "light";
        root.setAttribute("data-theme", nextTheme);
        localStorage.setItem("site-theme", nextTheme);
    });
}