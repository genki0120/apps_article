(() => {
  const progress = document.querySelector(".reading-progress span");

  const updateProgress = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    const pct = max > 0 ? scrollY / max : 0;
    if (progress) progress.style.width = Math.max(0, Math.min(100, pct * 100)) + "%";
  };

  addEventListener("scroll", updateProgress, { passive: true });
  addEventListener("resize", updateProgress, { passive: true });
  updateProgress();

  const targets = document.querySelectorAll(
    ".article-intro__contents, .article-app-card, .hero__copy, .logic__head, .logic-grid article, .why-steak__intro, .why-card, .rules__copy, .rule-detail, .steak-guide__head, .steak-row__copy, .temperature-style__intro, .temperature-band article, .style-strip article, .bottles__head, .bottle-card, .faq details, .closing__copy"
  );

  targets.forEach(el => el.classList.add("reveal"));

  if (!("IntersectionObserver" in window)) {
    targets.forEach(el => el.classList.add("is-visible"));
    return;
  }

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add("is-visible");
    });
  }, { threshold: .08 });

  targets.forEach(el => io.observe(el));
})();