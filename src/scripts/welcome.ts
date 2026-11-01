const welcome = document.querySelector<HTMLElement>('#welcome-screen');
const experience = document.querySelector<HTMLElement>('.experience');
const params = new URLSearchParams(window.location.search);
const returningToCatalogue = params.has('work') || params.has('embed');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (welcome && experience && !returningToCatalogue) {
  experience.inert = true;
  let ready = false;
  let minimumElapsed = false;
  let dismissed = false;
  const dismiss = () => {
    if (dismissed) return;
    dismissed = true;
    experience.inert = false;
    welcome.classList.add('is-leaving');
    window.setTimeout(() => {
      welcome.hidden = true;
      document.documentElement.classList.remove('has-welcome');
    }, reducedMotion ? 0 : 600);
  };
  window.addEventListener('room-ready', () => {
    ready = true;
    if (minimumElapsed) dismiss();
  }, { once: true });
  window.setTimeout(() => {
    minimumElapsed = true;
    if (ready) dismiss();
    else welcome.classList.add('is-waiting');
  }, reducedMotion ? 300 : 2000);
  // Reveal the room's own loading or error status if the model stalls.
  window.setTimeout(dismiss, 8000);
} else {
  if (welcome) welcome.hidden = true;
  document.documentElement.classList.remove('has-welcome');
}
