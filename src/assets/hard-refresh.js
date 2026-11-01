// Browsers do not expose a reliable hard-reload flag. Handle the common
// keyboard shortcuts explicitly so they restart the portfolio.
(() => {
  window.addEventListener('keydown', event => {
    const hardReload = ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === 'r') ||
      (event.ctrlKey && event.key === 'F5');
    if (!hardReload) return;
    event.preventDefault();
    location.replace('/');
  }, true);
})();
