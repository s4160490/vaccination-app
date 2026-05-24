// Animate progress bars on load
document.addEventListener('DOMContentLoaded', () => {
  const bars = document.querySelectorAll('.progress-fill, .region-bar-fill');
  bars.forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0%';
    requestAnimationFrame(() => {
      setTimeout(() => { bar.style.width = target; }, 80);
    });
  });
});
