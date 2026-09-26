(() => {
  const progress=document.querySelector(".reading-progress span");
  const update=()=>{
    const max=document.documentElement.scrollHeight-innerHeight;
    const pct=max>0?scrollY/max:0;
    if(progress) progress.style.width=Math.max(0,Math.min(100,pct*100))+"%";
  };
  addEventListener("scroll",update,{passive:true});
  update();

  const targets=document.querySelectorAll(
    ".article-intro__contents, .article-app-card, .hero__copy, .logic__head, .logic-grid article, .rules__copy, .materials__copy, .styles-section__head, .style-cards article, .wide-photo, .closing__copy"
  );
  targets.forEach(el=>el.classList.add("reveal"));

  const io=new IntersectionObserver(entries=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting) entry.target.classList.add("is-visible");
    });
  },{threshold:.08});
  targets.forEach(el=>io.observe(el));
})();