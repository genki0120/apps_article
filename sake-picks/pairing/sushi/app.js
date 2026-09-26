(() => {
  const progress = document.querySelector(".reading-progress span");

  const updateProgress = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    const pct = max > 0 ? scrollY / max : 0;
    if (progress) progress.style.width = Math.max(0, Math.min(100, pct * 100)) + "%";
  };

  addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  const revealTargets = document.querySelectorAll(
    ".opening > div:not(.opening__rule), .section-head, .principle-grid article, .fish-card__copy, .taste-grid article, .bottle-card, .availability, .faq details, .closing__copy"
  );

  revealTargets.forEach(el => el.classList.add("reveal"));

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add("is-visible");
    });
  }, { threshold: 0.1 });

  revealTargets.forEach(el => io.observe(el));

  document.querySelectorAll("details").forEach(detail => {
    detail.addEventListener("toggle", () => {
      if (!detail.open) return;
      document.querySelectorAll("details").forEach(other => {
        if (other !== detail) other.removeAttribute("open");
      });
    });
  });

  if (!matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const art = document.querySelectorAll("[data-shift]");
    const shiftArt = () => {
      art.forEach(el => {
        const rect = el.getBoundingClientRect();
        const strength = Number(el.dataset.shift || 5);
        const y = ((rect.top + rect.height / 2) - innerHeight / 2) / innerHeight;
        el.style.transform = "translate3d(0," + (y * strength) + "px,0)";
      });
    };
    addEventListener("scroll", shiftArt, { passive: true });
    shiftArt();
  }
})();