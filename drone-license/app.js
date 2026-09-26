const progress=document.querySelector(".reading-progress span");
const updateProgress=()=>{
  if(!progress)return;
  const h=document.documentElement;
  const max=h.scrollHeight-h.clientHeight;
  progress.style.width=(max>0?Math.min(100,(h.scrollTop/max)*100):0)+"%";
};
addEventListener("scroll",updateProgress,{passive:true});
updateProgress();

const io=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      entry.target.classList.add("is-visible");
      io.unobserve(entry.target);
    }
  });
},{threshold:.08});
document.querySelectorAll(".reveal").forEach(el=>io.observe(el));
