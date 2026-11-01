const dialog = document.querySelector<HTMLDialogElement>('#work-dialog')!;
const openButton = document.querySelector<HTMLButtonElement>('#open-work')!;
const closeButton = document.querySelector<HTMLButtonElement>('#close-work')!;
function updateWorkUrl(open: boolean) {
  const url = new URL(window.location.href);
  if (open) url.searchParams.set('work', '1');
  else url.searchParams.delete('work');
  history.replaceState(history.state, '', url);
}
function openWork() {
  if (!dialog.open) dialog.showModal();
  updateWorkUrl(true);
}
openButton.addEventListener('click', openWork);
window.addEventListener('open-projects', openWork);
closeButton.addEventListener('click', () => dialog.close());
dialog.addEventListener('close', () => updateWorkUrl(false));
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });

if (new URLSearchParams(location.search).has('work')) openWork();
