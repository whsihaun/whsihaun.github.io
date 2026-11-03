const root = document.documentElement;
const themeButton = document.getElementById('theme');
function updateThemeButton() {
  const dark = root.dataset.theme !== 'light';
  themeButton.querySelector('.theme-label').textContent = dark ? 'Light mode' : 'Dark mode';
  themeButton.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
}
updateThemeButton();
themeButton.addEventListener('click', () => {
  root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
  try { localStorage.setItem('theme', root.dataset.theme); } catch (_) {}
  updateThemeButton();
});
