const welcome = document.querySelector<HTMLElement>('#welcome-screen');
const experience = document.querySelector<HTMLElement>('.experience');
const returningToCatalogue = new URLSearchParams(window.location.search).has('work');
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
  const scramble = (time: number) => {
    lines.forEach((line, index) => {
      const text = originals[index];
      const start = index === 0 ? 0 : 1600;
      const duration = index === 0 ? 1400 : 1800;
      const progress = Math.max(0, Math.min(1, (time - start) / duration));
      const position = progress * (text.length + 3);
      const visible = Math.min(text.length, Math.floor(position));
      const settled = Math.max(0, Math.floor(position) - 3);
      line.textContent = Array.from(text.slice(0, visible), (char, i) => {
        if (char === ' ' || i < settled) return char;
        return glyphs[Math.floor(Math.random() * glyphs.length)];
      }).join('');
    });
  };
  if (!reducedMotion) {
    const started = performance.now();
    let previous = -100;
    const tick = (now: number) => {
      const elapsed = now - started;
      welcome.classList.toggle('is-typing-first', elapsed < 1400);
      welcome.classList.toggle('is-typing-second', elapsed >= 1600 && elapsed < 3400);
      if (now - previous >= 65) { scramble(elapsed); previous = now; }
      if (elapsed < 3450 && !dismissed) frame = requestAnimationFrame(tick);
      else { lines.forEach((line, index) => { line.textContent = originals[index]; }); welcome.classList.remove('is-typing-first', 'is-typing-second'); welcome.classList.add('is-resolved'); }
    };
    scramble(0);
    frame = requestAnimationFrame(tick);
  }
  const dismiss = () => {
    if (dismissed) return;
    dismissed = true;
    cancelAnimationFrame(frame);
    experience.inert = false;
    welcome.classList.add('is-leaving');
    window.setTimeout(() => { welcome.hidden = true; document.documentElement.classList.remove('has-welcome'); }, reducedMotion ? 0 : 700);
  };
  window.addEventListener('room-ready', () => { ready = true; if (minimumElapsed) dismiss(); }, { once: true });
  window.setTimeout(() => { minimumElapsed = true; if (ready) dismiss(); }, reducedMotion ? 300 : 4650);
  // A failed or stalled model request must never trap visitors on the intro.
  window.setTimeout(dismiss, 8000);
} else {
  if (welcome) welcome.hidden = true;
  document.documentElement.classList.remove('has-welcome');
}
