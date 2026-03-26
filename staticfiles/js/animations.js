'use strict';

/* SCROLL REVEAL */
function initScrollReveal(){
  if(!window.IntersectionObserver) return;
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target);}
    });
  },{threshold:.1});
  document.querySelectorAll('.reveal,.stagger').forEach(function(el){io.observe(el);});
}

/* NAVBAR SCROLL */
function initNavbar(){
  var nav=document.getElementById('mainNav');
  if(!nav)return;
  window.addEventListener('scroll',function(){nav.classList.toggle('scrolled',window.scrollY>50);},{passive:true});
}

/* RIPPLE on buttons */
function initRipple(){
  var st=document.createElement('style');
  st.textContent='.rhost{position:relative;overflow:hidden}.rdot{position:absolute;border-radius:50%;background:rgba(255,255,255,.25);transform:scale(0);animation:rpl .45s linear;pointer-events:none}@keyframes rpl{to{transform:scale(4);opacity:0}}';
  document.head.appendChild(st);
  document.addEventListener('click',function(e){
    var btn=e.target.closest('.btn-primary,.btn-auth,.btn-amber,[data-ripple]');
    if(!btn)return;
    btn.classList.add('rhost');
    var r=btn.getBoundingClientRect(),d=Math.max(r.width,r.height);
    var dot=document.createElement('span');dot.className='rdot';
    Object.assign(dot.style,{width:d+'px',height:d+'px',left:(e.clientX-r.left-d/2)+'px',top:(e.clientY-r.top-d/2)+'px'});
    btn.appendChild(dot);dot.addEventListener('animationend',function(){dot.remove();});
  });
}

/* AUTO-DISMISS MESSAGES */
function initMessages(){
  document.querySelectorAll('.message').forEach(function(el){
    setTimeout(function(){
      el.style.transition='opacity .4s';el.style.opacity='0';
      setTimeout(function(){el.remove();},420);
    },4500);
  });
}

document.addEventListener('DOMContentLoaded',function(){
  initScrollReveal();
  initNavbar();
  initRipple();
  initMessages();
});
