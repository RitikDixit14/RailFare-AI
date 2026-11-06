export function initCustomCursor(): () => void {
  const ring = document.getElementById('cursor-ring');
  const dot = document.getElementById('cursor-dot');
  if (!ring || !dot) return () => {};

  // Check if touch device
  if (window.matchMedia('(hover: none) and (pointer: coarse)').matches) {
    return () => {};
  }

  let mouseX = -100;
  let mouseY = -100;
  let ringX = -100;
  let ringY = -100;
  let animId: number;

  const onMouseMove = (e: MouseEvent) => {
    mouseX = e.clientX;
    mouseY = e.clientY;

    // Instant dot movement
    dot.style.transform = `translate(${mouseX}px, ${mouseY}px)`;
  };

  const onMouseEnterInteractive = () => {
    document.body.classList.add('cursor-hover');
  };

  const onMouseLeaveInteractive = () => {
    document.body.classList.remove('cursor-hover');
  };

  window.addEventListener('mousemove', onMouseMove, { passive: true });

  // Attach hover listeners to all clickable elements
  const interactiveSelectors = 'a, button, [role="button"], [role="listitem"], input, .module-row, .glass-card, .cta-launch-app';
  const attachInteractive = () => {
    document.querySelectorAll(interactiveSelectors).forEach((el) => {
      if ((el as HTMLElement).dataset.cursorBound) return;
      (el as HTMLElement).dataset.cursorBound = '1';
      el.addEventListener('mouseenter', onMouseEnterInteractive);
      el.addEventListener('mouseleave', onMouseLeaveInteractive);
    });
  };

  attachInteractive();
  const observer = new MutationObserver(attachInteractive);
  observer.observe(document.body, { childList: true, subtree: true });

  // Smooth lerp loop for the ring
  const render = () => {
    ringX += (mouseX - ringX) * 0.16;
    ringY += (mouseY - ringY) * 0.16;

    ring.style.transform = `translate(${ringX}px, ${ringY}px)`;
    animId = requestAnimationFrame(render);
  };
  render();

  return () => {
    cancelAnimationFrame(animId);
    window.removeEventListener('mousemove', onMouseMove);
    observer.disconnect();
  };
}

