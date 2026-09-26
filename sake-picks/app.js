(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  // ------------------------------------------------------------
  // Intro
  // ------------------------------------------------------------
  const intro = $(".intro");
  const counter = $(".intro__counter span");
  let n = 0;
  const timer = setInterval(() => {
    n += Math.ceil((100 - n) * 0.16);
    if (n >= 99) n = 100;
    if (counter) counter.textContent = String(n).padStart(2, "0");
    if (n >= 100) {
      clearInterval(timer);
      setTimeout(() => {
        intro?.classList.add("is-done");
        document.body.classList.add("is-loaded");
      }, 280);
    }
  }, 38);

  // ------------------------------------------------------------
  // Progress + header
  // ------------------------------------------------------------
  const progress = $(".scroll-progress span");
  const header = $(".header");

  const onScroll = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    const pct = max > 0 ? scrollY / max : 0;
    if (progress) progress.style.width = `${Math.max(0, Math.min(100, pct * 100))}%`;
    header?.classList.toggle("is-scrolled", scrollY > 80);

    // Generic parallax
    $$("[data-parallax]").forEach((el) => {
      const speed = Number(el.dataset.parallax || 0.08);
      const r = el.getBoundingClientRect();
      const center = r.top + r.height / 2 - innerHeight / 2;
      el.style.setProperty("--py", `${center * speed * -1}px`);
      el.style.transform = `translate3d(0, ${center * speed * -0.16}px, 0) scale(1.03)`;
    });

    // YMY-like full image expansion section
    const breakSection = $(".image-break");
    const breakMedia = $(".image-break__media");
    if (breakSection && breakMedia) {
      const r = breakSection.getBoundingClientRect();
      const travel = Math.max(1, r.height - innerHeight);
      const p = Math.max(0, Math.min(1, -r.top / travel));
      const scale = 0.72 + p * 0.28;
      const insetX = 12 - p * 12;
      const insetY = 10 - p * 10;
      breakMedia.style.transform = `scale(${scale})`;
      breakMedia.style.clipPath = `inset(${insetY}% ${insetX}% round 1px)`;
    }

    // Final CTA parallax
    const final = $(".final-cta");
    const finalMedia = $(".final-cta__visual");
    if (final && finalMedia) {
      const r = final.getBoundingClientRect();
      const p = Math.max(-1, Math.min(1, (r.top - innerHeight / 2) / innerHeight));
      finalMedia.style.transform = `translateY(${p * -24}px) scale(1.07)`;
    }
  };

  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  onScroll();

  // ------------------------------------------------------------
  // Custom cursor
  // ------------------------------------------------------------
  const orb = $(".cursor-orb");
  if (orb && matchMedia("(pointer:fine)").matches) {
    addEventListener("pointermove", (e) => {
      orb.style.transform = `translate(${e.clientX}px, ${e.clientY}px) translate(-50%,-50%)`;
    });
    $$("a,button,summary").forEach((el) => {
      el.addEventListener("pointerenter", () => orb.classList.add("is-hover"));
      el.addEventListener("pointerleave", () => orb.classList.remove("is-hover"));
    });
  }

  // ------------------------------------------------------------
  // Reveal
  // ------------------------------------------------------------
  $$(".manifesto__text, .story-scene__copy, .pairing__head, .pairing__result-copy, .craft-card, .source__copy, .faq__head")
    .forEach((el) => el.classList.add("js-reveal"));

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add("is-visible");
    });
  }, { threshold: 0.14 });
  $$(".js-reveal").forEach((el) => revealObserver.observe(el));

  // ------------------------------------------------------------
  // Story active state
  // ------------------------------------------------------------
  const scenes = $$(".story-scene");
  const storyButtons = $$(".story-step");

  const setStoryActive = (index) => {
    storyButtons.forEach((b, i) => b.classList.toggle("is-active", i === index));
  };

  const sceneObserver = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((e) => e.isIntersecting)
      .sort((a,b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    const i = Number(visible.target.dataset.scene);
    setStoryActive(i);
  }, { threshold: [0.35, 0.55, 0.75] });

  scenes.forEach((scene) => sceneObserver.observe(scene));
  storyButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const scene = $(`.story-scene[data-scene="${btn.dataset.storyStep}"]`);
      scene?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // ------------------------------------------------------------
  // Pairing selector
  // ------------------------------------------------------------
  const pairData = {
    white: {
      kanji: "白",
      kicker: "CLEAN · FRUITY · LIGHT",
      title: "White fish likes precision.",
      body: "Keep the aroma restrained and the finish bright. A polished Ginjo or Junmai Daiginjo can lift sea bream, flounder and scallop without covering their sweetness.",
      meters: [72, 28, 38],
      image: "White fish pairing visual"
    },
    tuna: {
      kanji: "鮪",
      kicker: "UMAMI · BODY · ACIDITY",
      title: "Fatty tuna can carry more depth.",
      body: "Toro brings fat and sweetness. Sake with savory depth, structure or acidity can refresh the palate while staying present beside the richness.",
      meters: [36, 78, 86],
      image: "Fatty tuna pairing visual"
    },
    salmon: {
      kanji: "鮭",
      kicker: "ROUND · FRUITY · BALANCED",
      title: "Salmon rewards softness.",
      body: "Salmon has both richness and sweetness. Look for rounded texture, approachable fruit and enough acidity to keep the finish lively.",
      meters: [66, 61, 56],
      image: "Salmon pairing visual"
    },
    shellfish: {
      kanji: "貝",
      kicker: "BRIGHT · CRISP · MINERAL",
      title: "Shellfish wants clarity.",
      body: "Oysters, scallops and clams can show salinity and delicate sweetness. A clean, bright sake keeps those flavors precise and lengthens the finish.",
      meters: [48, 24, 46],
      image: "Shellfish pairing visual"
    },
    spicy: {
      kanji: "辛",
      kicker: "SOFT · AROMATIC · GENTLE",
      title: "Spice likes a softer landing.",
      body: "A little fruit and softness can round heat. Avoid an aggressively alcoholic finish that makes spice feel sharper than it needs to.",
      meters: [80, 44, 30],
      image: "Spicy roll pairing visual"
    }
  };

  const choices = $$(".pairing-choice");
  const result = $(".pairing__result");
  const updatePairing = (key) => {
    const d = pairData[key];
    if (!d || !result) return;

    choices.forEach((c) => {
      const active = c.dataset.pair === key;
      c.classList.toggle("is-active", active);
      c.setAttribute("aria-selected", String(active));
    });

    $(".js-pair-kanji").textContent = d.kanji;
    $(".js-pair-kicker").textContent = d.kicker;
    $(".js-pair-title").textContent = d.title;
    $(".js-pair-body").textContent = d.body;
    $(".js-pair-image").textContent = d.image;

    $$(".js-meter").forEach((m, i) => {
      const v = d.meters[i];
      m.style.setProperty("--meter", `${v}%`);
      const em = m.closest(".meter")?.querySelector("em");
      if (em) em.textContent = String(v);
    });

    result.animate(
      [{ opacity: 0.55, transform: "translateY(10px)" }, { opacity: 1, transform: "translateY(0)" }],
      { duration: 520, easing: "cubic-bezier(.16,1,.3,1)" }
    );
  };

  choices.forEach((choice) => choice.addEventListener("click", () => updatePairing(choice.dataset.pair)));

  // ------------------------------------------------------------
  // Bottle carousel
  // ------------------------------------------------------------
  const carousel = $("[data-carousel]");
  const prev = $("[data-carousel-prev]");
  const next = $("[data-carousel-next]");

  const moveCarousel = (dir) => {
    if (!carousel) return;
    const card = $(".bottle-card", carousel);
    const amount = card ? card.getBoundingClientRect().width + 20 : innerWidth * 0.7;
    carousel.scrollBy({ left: amount * dir, behavior: "smooth" });
  };
  prev?.addEventListener("click", () => moveCarousel(-1));
  next?.addEventListener("click", () => moveCarousel(1));

  // ------------------------------------------------------------
  // FAQ: one at a time
  // ------------------------------------------------------------
  $$("details").forEach((detail) => {
    detail.addEventListener("toggle", () => {
      if (!detail.open) return;
      $$("details").forEach((other) => {
        if (other !== detail) other.removeAttribute("open");
      });
    });
  });
})();