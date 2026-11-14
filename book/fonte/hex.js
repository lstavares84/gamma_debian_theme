// GAMMA Debian, mockups: auxiliar de hexágonos. Criação original.
function hexPts(cx, cy, r) {
  const w = Math.sqrt(3) / 2 * r;
  return [[cx, cy - r], [cx + w, cy - r / 2], [cx + w, cy + r / 2], [cx, cy + r], [cx - w, cy + r / 2], [cx - w, cy - r / 2]]
    .map(p => p[0].toFixed(2) + ',' + p[1].toFixed(2)).join(' ');
}
const HEX_KIND = {
  ok: ['#0A300C', '#78FF5A'], wa: ['#3C2C00', '#FFBE00'], cr: ['#480404', '#FF3C32'],
  nd: ['#081209', '#1E341E'], ne: ['#081C0A', '#40783C'], on: ['#78FF5A', '#78FF5A'],
  off: ['none', '#234B23'], line: ['none', '#6EAA6E'], ice: ['none', '#BEFFAA'], acc: ['none', '#78FF5A'],
  amb: ['none', '#FFBE00'], red: ['none', '#FF3C32']
};
// <i class="hx" data-s="16" data-k="ok" data-t="texto" data-g="1"></i>
document.querySelectorAll('.hx').forEach(el => {
  const s = +el.dataset.s || 16, k = HEX_KIND[el.dataset.k || 'ok'], sw = +(el.dataset.w || 1.2);
  const r = s / 2 - sw;
  const glow = el.dataset.g ? `filter="drop-shadow(0 0 3px ${k[1]})"` : '';
  const t = el.dataset.t ? `<text x="${s / 2}" y="${s / 2}" text-anchor="middle" dominant-baseline="central" fill="${el.dataset.tc || k[1]}" style="font:700 ${el.dataset.ts || s * .45}px ${el.dataset.tf || 'JetBrains Mono'}">${el.dataset.t}</text>` : '';
  el.innerHTML = `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}"><polygon ${glow} points="${hexPts(s / 2, s / 2, r)}" fill="${k[0]}" stroke="${k[1]}" stroke-width="${sw}"/>${t}</svg>`;
  el.style.display = 'inline-block'; el.style.width = s + 'px'; el.style.height = s + 'px'; el.style.verticalAlign = 'middle';
});
document.querySelectorAll('svg [data-hex]').forEach(p => {
  const [cx, cy, r] = p.dataset.hex.split(',').map(Number);
  p.setAttribute('points', hexPts(cx, cy, r));
});
