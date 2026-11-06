export function initPipelineGraph(): () => void {
  const card = document.getElementById('hero-pipeline-card');
  const logContainer = document.getElementById('telemetry-log-entries');
  if (!logContainer) return () => {};

  // Sample realistic runs based on real repo trains & fallback logic
  const sampleRuns = [
    { train: '#12004 NDLS→LKO', model: 'RF_MODEL', time: '82ms', surge: '+1.35x', status: '200' },
    { train: '#12424 NDLS→DBRG', model: 'RF_MODEL', time: '114ms', surge: '+1.50x', status: '200' },
    { train: '#22692 NZM→SBC', model: 'RF_MODEL', time: '94ms', surge: '+1.10x', status: '200' },
    { train: '#12259 BKN→SDAH', model: 'RF_MODEL', time: '88ms', surge: '+1.25x', status: '200' },
    { train: '#12952 NDLS→MMCT', model: 'MASTER_CSV', time: '42ms', surge: '1.00x', status: '200' },
    { train: '#12301 HWH→NDLS', model: 'RF_MODEL', time: '76ms', surge: '+1.40x', status: '200' },
    { train: '#18310 JAT→SBP', model: 'RF_MODEL', time: '102ms', surge: '+1.20x', status: '200' },
    { train: '#12002 NDLS→BPL', model: 'RF_MODEL', time: '65ms', surge: '+1.30x', status: '200' },
  ];

  let runIndex = 0;

  const appendLogRow = () => {
    const run = sampleRuns[runIndex % sampleRuns.length];
    runIndex++;

    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0] + '.' + String(Math.floor(now.getMilliseconds() / 100));

    const row = document.createElement('div');
    row.className = 'log-row';
    row.innerHTML = `
      <span class="log-time">${timeStr}</span>
      <span class="log-event">${run.train}</span>
      <span class="log-model">${run.model}</span>
      <span class="log-duration">${run.time}</span>
      <span class="log-surge">${run.surge}</span>
    `;

    logContainer.prepend(row);

    // Keep max 4 rows
    while (logContainer.children.length > 4) {
      logContainer.removeChild(logContainer.lastElementChild!);
    }
  };

  // Seed initial 3 rows
  appendLogRow();
  appendLogRow();
  appendLogRow();

  // Interval to add rows every 2.8s
  const logInterval = setInterval(appendLogRow, 2800);

  // 3D Tilt on Mouse over card (Desktop only)
  let tiltCleanup = () => {};
  if (card && window.matchMedia('(min-width: 769px)').matches) {
    const onMouseMove = (e: MouseEvent) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      const rotY = (x / (rect.width / 2)) * 8;
      const rotX = -(y / (rect.height / 2)) * 8;
      card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(-2px)`;
    };

    const onMouseLeave = () => {
      card.style.transform = `perspective(1000px) rotateY(-4deg) rotateX(3deg)`;
    };

    card.addEventListener('mousemove', onMouseMove, { passive: true });
    card.addEventListener('mouseleave', onMouseLeave);

    tiltCleanup = () => {
      card.removeEventListener('mousemove', onMouseMove);
      card.removeEventListener('mouseleave', onMouseLeave);
    };
  }

  return () => {
    clearInterval(logInterval);
    tiltCleanup();
  };
}

