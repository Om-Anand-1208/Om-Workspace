export {};

const monitor = document.querySelector<HTMLDialogElement>('#monitor-window')!;
const laptop = document.querySelector<HTMLDialogElement>('#laptop-window')!;
const terminalBody = monitor.querySelector<HTMLElement>('.terminal-body')!;
const terminalTyped = monitor.querySelector<HTMLElement>('#terminal-typed')!;
const terminalResult = monitor.querySelector<HTMLElement>('#terminal-result')!;
const laptopBody = laptop.querySelector<HTMLElement>('.laptop-window-body')!;
const laptopLines = Array.from(laptop.querySelectorAll<HTMLElement>('.laptop-window-copy span'));
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let frame = 0;
let timer = 0;

function cancelAnimation() { cancelAnimationFrame(frame); window.clearTimeout(timer); }

function playTerminal() {
  cancelAnimation();
  terminalTyped.textContent = '';
  terminalResult.hidden = true;
  if (reducedMotion) { terminalTyped.textContent = 'fastfetch'; terminalResult.hidden = false; return; }
  const command = 'fastfetch';
  let index = 0;
  const type = () => {
    terminalTyped.textContent = command.slice(0, ++index);
    if (index < command.length) timer = window.setTimeout(type, 95);
    else timer = window.setTimeout(() => { terminalResult.hidden = false; }, 240);
  };
  timer = window.setTimeout(type, 280);
}

function playWelcome() {
  cancelAnimation();
  const originals = ["Hi, I'm Om Anand.", 'Welcome to my workspace.'];
  const glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz*+?{}#$%&/!';
  laptopLines.forEach(line => { line.textContent = ''; });
  if (reducedMotion) { laptopLines.forEach((line, i) => { line.textContent = originals[i]; }); return; }
  const startTime = performance.now();
  let previous = -100;
  const tick = (now: number) => {
    const elapsed = now - startTime;
    if (elapsed - previous >= 65) {
      laptopLines.forEach((line, index) => {
        const text = originals[index];
        const start = index === 0 ? 0 : 1600;
        const duration = index === 0 ? 1400 : 1800;
        const progress = Math.max(0, Math.min(1, (elapsed - start) / duration));
        const position = progress * (text.length + 3);
        const visible = Math.min(text.length, Math.floor(position));
        const settled = Math.max(0, Math.floor(position) - 3);
        line.textContent = Array.from(text.slice(0, visible), (character, i) =>
          character === ' ' || i < settled ? character : glyphs[Math.floor(Math.random() * glyphs.length)]
        ).join('');
      });
      previous = elapsed;
    }
    if (elapsed < 3450) frame = requestAnimationFrame(tick);
    else laptopLines.forEach((line, i) => { line.textContent = originals[i]; });
  };
  frame = requestAnimationFrame(tick);
}

function openScreen(kind: 'monitor' | 'laptop') {
  const dialog = kind === 'monitor' ? monitor : laptop;
  if (!dialog.open) dialog.showModal();
  if (kind === 'monitor') playTerminal(); else playWelcome();
}
window.addEventListener('open-room-screen', event => {
  const kind = (event as CustomEvent<'monitor' | 'laptop'>).detail;
  if (kind === 'monitor' || kind === 'laptop') openScreen(kind);
});
document.querySelector('#open-monitor')?.addEventListener('click', () => openScreen('monitor'));
document.querySelector('#open-laptop')?.addEventListener('click', () => openScreen('laptop'));
terminalBody.addEventListener('click', playTerminal);
laptopBody.addEventListener('click', playWelcome);
[monitor, laptop].forEach(dialog => {
  dialog.querySelector('.screen-window-close')?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', cancelAnimation);
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
});
