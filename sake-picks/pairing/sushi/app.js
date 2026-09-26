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
    ".hero__copy, .quick-answer__copy, .section-title, .why-intro__copy, .why-chapter__copy, .history-card, .rules-section__intro, .rule-grid article, .pairing-row__copy, .rice-section__intro, .seasoning-grid article, .temperature-section__intro, .temperature-card, .bottles__intro, .bottle-card, .availability, .ordering-section__intro, .order-scripts article, .faq details, .closing__copy"
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