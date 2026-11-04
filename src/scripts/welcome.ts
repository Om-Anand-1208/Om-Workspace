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
  let frame = 0;
  const lines = Array.from(welcome.querySelectorAll<HTMLElement>('.welcome-line'));
  const originals = lines.map(line => line.textContent ?? '');
  const glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz*+?{}#$%&/!';

  if (!reducedMotion) {
    const started = performance.now();
    let previous = -100;
    const tick = (now: number) => {
      const elapsed = now - started;
      welcome.classList.toggle('is-typing-first', elapsed < 1400);
      welcome.classList.toggle('is-typing-second', elapsed >= 1600 && elapsed < 3400);
      if (now - previous >= 65) {
        lines.forEach((line, index) => {
          const text = originals[index];
          const start = index === 0 ? 0 : 1600;
          const duration = index === 0 ? 1400 : 1800;
          const progress = Math.max(0, Math.min(1, (elapsed - start) / duration));
          const position = progress * (text.length + 3);
          const visible = Math.min(text.length, Math.floor(position));
          const settled = Math.max(0, Math.floor(position) - 3);
          line.textContent = Array.from(text.slice(0, visible), (char, i) =>
            char === ' ' || i < settled ? char : glyphs[Math.floor(Math.random() * glyphs.length)]
          ).join('');
        });
        previous = now;
      }
      if (elapsed < 3450 && !dismissed) frame = requestAnimationFrame(tick);
      else {
        lines.forEach((line, index) => { line.textContent = originals[index]; });
        welcome.classList.remove('is-typing-first', 'is-typing-second');
        welcome.classList.add('is-resolved');
      }
    };
    lines.forEach(line => { line.textContent = ''; });
    welcome.classList.add('is-animating');
    frame = requestAnimationFrame(tick);
  } else {
    welcome.classList.add('is-animating', 'is-resolved');
  }

  const dismiss = () => {
    if (dismissed) return;
    dismissed = true;
    cancelAnimationFrame(frame);
    experience.classList.add('is-revealing');
    welcome.classList.add('is-leaving');
    window.setTimeout(() => {
      experience.inert = false;
      welcome.hidden = true;
      document.documentElement.classList.remove('has-welcome');
    }, reducedMotion ? 0 : 1000);
  };
  window.addEventListener('room-ready', () => {
    ready = true;
    if (minimumElapsed) dismiss();
  }, { once: true });
  window.setTimeout(() => {
    minimumElapsed = true;
    if (ready) dismiss();
    else welcome.classList.add('is-waiting');
  }, reducedMotion ? 150 : 3900);
  // Reveal the room's own loading or error status if the model stalls.
  window.setTimeout(dismiss, 10000);
} else {
  if (welcome) welcome.hidden = true;
  document.documentElement.classList.remove('has-welcome');
}
