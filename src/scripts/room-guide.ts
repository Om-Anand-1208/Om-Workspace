const guide = document.querySelector<HTMLElement>('#room-guide');
const openButton = document.querySelector<HTMLButtonElement>('#open-guide');
const closeButton = document.querySelector<HTMLButtonElement>('#close-guide');

closeButton?.addEventListener('click', () => {
  if (!guide || !openButton) return;
  guide.hidden = true;
  openButton.hidden = false;
  openButton.focus();
});
openButton?.addEventListener('click', () => {
  if (!guide) return;
  guide.hidden = false;
  openButton.hidden = true;
  closeButton?.focus();
});

export {};
