const dialog = document.querySelector<HTMLDialogElement>('#work-dialog')!;
const openButton = document.querySelector<HTMLButtonElement>('#open-work')!;
const closeButton = document.querySelector<HTMLButtonElement>('#close-work')!;
function openWork() { if (!dialog.open) dialog.showModal(); }
openButton.addEventListener('click', openWork);
window.addEventListener('open-projects', openWork);
closeButton.addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });

if (new URLSearchParams(location.search).has('work')) openWork();
