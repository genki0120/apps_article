(() => {
  const progress = document.querySelector(".reading-progress span");

  const updateProgress = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    const pct = max > 0 ? scrollY / max : 0;
    if (progress) progress.style.width = Math.max(0, Math.min(100, pct * 100)) + "%";
  };

  const addExtendedToc = () => {
    const nav = document.querySelector(".article-intro__list");
    if (!nav || nav.querySelector('a[href="#choose-by-steak"]')) return;

    const items = [
      ["05", "#choose-by-steak", "Choose by Steak", "Filet, ribeye, Wagyu & char"],
      ["06", "#temperature-style", "Temperature & Style", "Chilled, room temperature, warmed"],
      ["07", "#bottles", "Curated Bottles", "Four food-first directions"],
      ["08", "#faq", "FAQ & Next Step", "Before your next steak night"],
    ];

    items.forEach(([no, href, title, subtitle]) => {
      const a = document.createElement("a");
      a.href = href;
      a.innerHTML = "<span>" + no + "</span><strong>" + title + "</strong><small>" + subtitle + "</small>";
      nav.appendChild(a);
    });
  };

  const addContinuationStyles = () => {
    if (document.querySelector('link[data-steak-continuation]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "./content-05-08.css?v=20260926";
    link.dataset.steakContinuation = "true";
    document.head.appendChild(link);
  };

  const setupReveal = () => {
    const targets = document.querySelectorAll(
      ".article-intro__contents, .article-app-card, .hero__copy, .logic__head, .logic-grid article, .why-steak__intro, .why-card, .rules__copy, .rule-detail, .steak-guide__head, .steak-row__copy, .temperature-style__intro, .temperature-band article, .style-strip article, .bottles__head, .bottle-card, .faq details, .closing__copy"
    );

    targets.forEach(el => {
      if (!el.classList.contains("reveal")) el.classList.add("reveal");
    });

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
  };

  const loadContinuation = async () => {
    addContinuationStyles();
    addExtendedToc();

    const main = document.querySelector("main");
    if (!main || document.querySelector("#choose-by-steak")) {
      setupReveal();
      return;
    }

    try {
      const response = await fetch("./content-05-08.html?v=20260926", { cache: "no-cache" });
      if (!response.ok) throw new Error("Continuation load failed");
      const html = await response.text();
      main.insertAdjacentHTML("beforeend", html);
    } catch (error) {
      console.error(error);
    }

    setupReveal();
    updateProgress();
  };

  addEventListener("scroll", updateProgress, { passive: true });
  addEventListener("resize", updateProgress, { passive: true });
  updateProgress();
  loadContinuation();
})();