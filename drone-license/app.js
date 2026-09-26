const header = document.querySelector('[data-header]');
window.addEventListener('scroll', () => header?.classList.toggle('is-scrolled', window.scrollY > 12), { passive: true });

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

const tabs = document.querySelector('[data-tabs]');
if (tabs) {
  const buttons = [...tabs.querySelectorAll('[data-tab]')];
  const panels = [...tabs.querySelectorAll('[data-panel]')];
  buttons.forEach((button) => button.addEventListener('click', () => {
    const id = button.dataset.tab;
    buttons.forEach(b => b.classList.toggle('is-active', b === button));
    panels.forEach(p => p.classList.toggle('is-active', p.dataset.panel === id));
  }));
}

const roadmap = document.querySelector('[data-roadmap]');
if (roadmap) {
  const line = roadmap.querySelector('.roadmap__line span');
  const steps = [...roadmap.querySelectorAll('.roadmap-step')];
  const update = () => {
    const rect = roadmap.getBoundingClientRect();
    const vh = window.innerHeight;
    const raw = (vh * 0.72 - rect.top) / Math.max(rect.height, 1);
    const progress = Math.max(0, Math.min(1, raw));
    if (line) line.style.width = `${progress * 100}%`;
    const activeIndex = Math.min(steps.length - 1, Math.max(0, Math.floor(progress * steps.length)));
    steps.forEach((step, i) => step.classList.toggle('is-active', i <= activeIndex));
  };
  update();
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
}

document.querySelectorAll('.faq-list details').forEach((detail) => {
  detail.addEventListener('toggle', () => {
    if (!detail.open) return;
    document.querySelectorAll('.faq-list details').forEach((other) => {
      if (other !== detail) other.open = false;
    });
  });
});

// LICENSE FLOW 2026-09-26
const licenseFlow = document.querySelector('[data-license-flow]');
if (licenseFlow) {
  const track = licenseFlow.querySelector('.license-flow__track i');
  const steps = [...licenseFlow.querySelectorAll('article')];
  const updateLicenseFlow = () => {
    const rect = licenseFlow.getBoundingClientRect();
    const vh = window.innerHeight;
    const raw = (vh * 0.72 - rect.top) / Math.max(rect.height, 1);
    const progress = Math.max(0, Math.min(1, raw));
    if (track) track.style.width = `${progress * 100}%`;
    const activeIndex = Math.min(steps.length - 1, Math.max(0, Math.floor(progress * steps.length)));
    steps.forEach((step, i) => step.classList.toggle('is-active', i <= activeIndex));
  };
  updateLicenseFlow();
  window.addEventListener('scroll', updateLicenseFlow, { passive: true });
  window.addEventListener('resize', updateLicenseFlow);
}
