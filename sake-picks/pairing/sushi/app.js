(() => {
  const progress = document.querySelector(".reading-progress span");

  const updateProgress = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    const pct = max > 0 ? scrollY / max : 0;
    if (progress) progress.style.width = Math.max(0, Math.min(100, pct * 100)) + "%";
  };

  addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  const targets = document.querySelectorAll(
    ".hero__copy, .split-story__copy, .section-title, .principle-grid article, .pairing-row__copy, .taste-grid article, .bottle-card, .availability, .faq details, .closing__copy"
  );

  targets.forEach(el => el.classList.add("reveal"));

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add("is-visible");
    });
  }, { threshold: 0.08 });

  targets.forEach(el => io.observe(el));

  document.querySelectorAll("details").forEach(detail => {
    detail.addEventListener("toggle", () => {
      if (!detail.open) return;
      document.querySelectorAll("details").forEach(other => {
        if (other !== detail) other.removeAttribute("open");
      });
    });
  });
})();