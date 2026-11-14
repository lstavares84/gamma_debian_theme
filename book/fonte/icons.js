// GAMMA Debian, mockups: ícones de traço simples. Criação original.
document.body.insertAdjacentHTML('afterbegin', `
<svg width="0" height="0" style="position:absolute">
 <defs>
  <symbol id="i-term" viewBox="0 0 24 24"><rect x="2.5" y="4.5" width="19" height="15" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 9l3 3-3 3M11 15h6" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-folder" viewBox="0 0 24 24"><path d="M2.5 6.5h7l2 2h10v11h-19z" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18" fill="none" stroke="currentColor" stroke-width="1.2"/></symbol>
  <symbol id="i-edit" viewBox="0 0 24 24"><path d="M5 3.5h10l4 4v13H5z M8 10h8M8 13h8M8 16h5" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-gear" viewBox="0 0 24 24"><polygon points="12,3 19.8,7.5 19.8,16.5 12,21 4.2,16.5 4.2,7.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-chart" viewBox="0 0 24 24"><path d="M3 20.5h18M3 16l5-6 4 4 4-8 5 5" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-search" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M15 15l5.5 5.5" stroke="currentColor" stroke-width="1.6"/></symbol>
  <symbol id="i-lock" viewBox="0 0 24 24"><rect x="5" y="10.5" width="14" height="10" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-power" viewBox="0 0 24 24"><path d="M12 3v8M7 6.5a7.5 7.5 0 1 0 10 0" fill="none" stroke="currentColor" stroke-width="1.6"/></symbol>
  <symbol id="i-image" viewBox="0 0 24 24"><rect x="3" y="4.5" width="18" height="15" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3 16l5-5 4 4 3-3 6 6" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-music" viewBox="0 0 24 24"><path d="M9 18V5l11-2v13" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="6.5" cy="18" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="17.5" cy="16" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-code" viewBox="0 0 24 24"><path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-office" viewBox="0 0 24 24"><rect x="4" y="3.5" width="16" height="17" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 8h8M8 12h8M8 16h4" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-star" viewBox="0 0 24 24"><path d="M12 3l2.7 6 6.3.6-4.8 4.2 1.4 6.2L12 16.8 6.4 20l1.4-6.2L3 9.6 9.3 9z" fill="none" stroke="currentColor" stroke-width="1.4"/></symbol>
  <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-sys" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 20h8M12 16v4" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-warn" viewBox="0 0 24 24"><path d="M12 7v6M12 16v1.5" stroke="currentColor" stroke-width="2"/></symbol>
  <symbol id="i-close" viewBox="0 0 24 24"><path d="M7 7l10 10M17 7L7 17" stroke="currentColor" stroke-width="1.6"/></symbol>
  <symbol id="i-min" viewBox="0 0 24 24"><path d="M7 15h10" stroke="currentColor" stroke-width="1.6"/></symbol>
  <symbol id="i-max" viewBox="0 0 24 24"><rect x="7.5" y="7.5" width="9" height="9" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-down" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.6"/></symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><path d="M6.5 12.5l3.5 3.5 7.5-8" fill="none" stroke="currentColor" stroke-width="2.2"/></symbol>
  <symbol id="i-vol" viewBox="0 0 24 24"><path d="M4 9.5h4l5-4v13l-5-4H4z M16.5 9a4 4 0 0 1 0 6" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
  <symbol id="i-net" viewBox="0 0 24 24"><path d="M12 19V5M7 10l5-5 5 5M4 19h16" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
 </defs>
</svg>`);
document.querySelectorAll('i[data-i]').forEach(el => {
  const s = el.dataset.s || 16;
  el.innerHTML = `<svg width="${s}" height="${s}"><use href="#i-${el.dataset.i}"/></svg>`;
  el.style.display = 'inline-block'; el.style.verticalAlign = 'middle'; el.style.width = s + 'px'; el.style.height = s + 'px';
});
