// ── DATA LAYER ──────────────────────────────────────────────
const DEFAULT_DB = {
  morning:{
    "protein powder":{"serving":100,"kcal":370,"protein":29,"carbs":50,"fat":8.24},
    "banana":{"serving":1,"kcal":89,"protein":1.1,"carbs":23,"fat":0.3},
    "channa":{"serving":50,"kcal":180,"protein":9,"carbs":30,"fat":3},
    "chia seeds":{"serving":100,"kcal":490,"protein":16,"carbs":44,"fat":31},
    "sunflower seeds":{"serving":100,"kcal":582,"protein":19,"carbs":24,"fat":55},
    "flax seeds":{"serving":100,"kcal":534,"protein":18,"carbs":29,"fat":42},
    "pumpkin seeds":{"serving":100,"kcal":446,"protein":19,"carbs":54,"fat":19},
    "honey":{"serving":100,"kcal":320,"protein":0,"carbs":80,"fat":0}
  },
  lunch:{
    "oats yogabar":{"serving":50,"kcal":177,"protein":13,"carbs":26,"fat":3.6},
    "oats pintola":{"serving":50,"kcal":196,"protein":12.5,"carbs":27.3,"fat":3.9},
    "oats MB":{"serving":100,"kcal":386,"protein":12,"carbs":68,"fat":9.5},
    "milk":{"serving":100,"kcal":87,"protein":3.2,"carbs":5,"fat":6},
    "milk low fat":{"serving":100,"kcal":47,"protein":3.3,"carbs":5,"fat":1.5},
    "peanut butter":{"serving":32,"kcal":192,"protein":9.6,"carbs":5.4,"fat":14.7},
    "sattu":{"serving":50,"kcal":205.5,"protein":11,"carbs":23,"fat":6}
  },
  evening:{
    "egg":{"serving":1,"kcal":78,"protein":5.5,"carbs":0.4,"fat":5.3}
  },
  dinner:{
    "roti":{"serving":1,"kcal":90,"protein":2.5,"carbs":16.5,"fat":1.5},
    "rice":{"serving":100,"kcal":130,"protein":2.5,"carbs":28,"fat":0.3},
    "paneer bhurji":{"serving":250,"kcal":290,"protein":15,"carbs":20,"fat":20}
  }
};

const DEFAULT_SETTINGS = {goal_kcal:2500,goal_protein:120,bulk_mode:false,light_mode:false,gemini_key:''};

function LS(key,def){
  try{const v=localStorage.getItem(key);return v?JSON.parse(v):def;}catch{return def;}
}
function LSset(key,val){try{localStorage.setItem(key,JSON.stringify(val));}catch{}}

let nf_username = localStorage.getItem('nf_username') || '';

let db = LS('nf_db', DEFAULT_DB);
let settings = LS('nf_settings', DEFAULT_SETTINGS);
let mealLog = LS('nf_log', []);
let weightLog = LS('nf_weight', []);
let waterLog = LS('nf_water', {});
let chatSessions = LS('nf_sessions', [{id: Date.now(), title: 'New Chat', messages: []}]);
let currentSessionId = chatSessions.length > 0 ? chatSessions[0].id : Date.now();
if (chatSessions.length === 0) chatSessions.push({id: currentSessionId, title: 'New Chat', messages: []});

function saveAll(){
  LSset('nf_db',db);
  LSset('nf_settings',settings);
  LSset('nf_log',mealLog);
  LSset('nf_weight',weightLog);
  LSset('nf_water',waterLog);
  LSset('nf_sessions',chatSessions);
  if(window.syncToCloud) window.syncToCloud();
}

function today(){return new Date().toISOString().slice(0,10)}

function getGoals(){
  const k=settings.goal_kcal, p=settings.goal_protein;
  return settings.bulk_mode?{kcal:k*1.2,protein:p*1.2}:{kcal:k,protein:p};
}

function todayTotals(){
  const t=today();
  const entries=mealLog.filter(e=>e.date===t);
  const sum={kcal:0,protein:0,carbs:0,fat:0,count:entries.length};
  entries.forEach(e=>{sum.kcal+=e.kcal;sum.protein+=e.protein;sum.carbs+=e.carbs;sum.fat+=e.fat;});
  return sum;
}

// ── TOAST ─────────────────────────────────────────────────
let toastTimer;
function toast(msg,type='green'){
  const t=document.getElementById('toast');
  const d=document.getElementById('toast-dot');
  const m=document.getElementById('toast-msg');
  d.className='toast-dot '+type;
  m.textContent=msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>t.classList.remove('show'),2800);
}

// ── NAVIGATION ────────────────────────────────────────────
const PAGE_TITLES={dash:'Dashboard',log:'Log Meal',custom:'Quick Add',weight:'Trends',foods:'Food Database',settings:'Settings',ai:'AI Coach'};
function gotoPage(name,el){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.getElementById('page-'+name).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  if(el)el.classList.add('active');
  document.getElementById('page-title').textContent=PAGE_TITLES[name]||name;
  if(name==='dash')refreshDash();
  if(name==='log')renderLogForm();
  if(name==='weight')renderTrends();
  if(name==='foods')renderDBList('morning');
  if(name==='settings')initSettings();
  if(name==='custom')renderCustomRemaining();
}

// ── BULK MODE ─────────────────────────────────────────────
function toggleBulk(){
  settings.bulk_mode=!settings.bulk_mode;
  saveAll();
  syncBulkUI();
  refreshDash();
  toast(settings.bulk_mode?'Bulk mode ON — goals +20%':'Bulk mode OFF',settings.bulk_mode?'green':'red');
}
function syncBulkUI(){
  ['bulk-pill','bulk-pill2'].forEach(id=>{
    const el=document.getElementById(id);
    if(el)el.classList.toggle('on',settings.bulk_mode);
  });
  const tPill=document.getElementById('theme-pill');
  if(tPill) tPill.classList.toggle('on',settings.light_mode);
  applyTheme();
}

function applyTheme(){
  if(settings.light_mode) document.documentElement.classList.add('light-mode');
  else document.documentElement.classList.remove('light-mode');
}

function toggleTheme(){
  settings.light_mode = !settings.light_mode;
  syncBulkUI();
  saveAll();
  toast(settings.light_mode ? 'Light mode ON' : 'Light mode OFF');
}

syncBulkUI();

// ── DASHBOARD ─────────────────────────────────────────────
const CIRC=2*Math.PI*33;
function setRing(id,pct){
  const el=document.getElementById(id);
  if(!el)return;
  const offset=CIRC*(1-Math.min(pct,1));
  el.style.strokeDasharray=CIRC;
  el.style.strokeDashoffset=offset;
}

function refreshDash(){
  const waterEl = document.getElementById('water-val');
  if(waterEl) waterEl.textContent = waterLog[today()] || 0;

  const t=todayTotals();
  const g=getGoals();
  const calPct=g.kcal>0?t.kcal/g.kcal:0;
  const proPct=g.protein>0?t.protein/g.protein:0;

  setRing('cal-ring',calPct);
  setRing('pro-ring',proPct);
  document.getElementById('cal-pct').textContent=Math.round(calPct*100)+'%';
  document.getElementById('pro-pct').textContent=Math.round(proPct*100)+'%';
  document.getElementById('cal-val').textContent=Math.round(t.kcal);
  document.getElementById('pro-val').textContent=Math.round(t.protein);
  document.getElementById('cal-goal').textContent='/ '+Math.round(g.kcal)+' kcal';
  document.getElementById('pro-goal').textContent='/ '+Math.round(g.protein)+' g';
  document.getElementById('dash-carbs').innerHTML=Math.round(t.carbs)+'<span style="font-size:12px">g</span>';
  document.getElementById('dash-fat').innerHTML=Math.round(t.fat)+'<span style="font-size:12px">g</span>';
  document.getElementById('dash-meals').textContent=t.count;
  const rem=Math.round(g.kcal-t.kcal);
  const remEl=document.getElementById('dash-remaining');
  remEl.textContent=rem;
  remEl.style.color=rem<0?'var(--red)':'var(--text)';

  document.getElementById('prog-cal').style.width=Math.min(calPct*100,100)+'%';
  document.getElementById('prog-pro').style.width=Math.min(proPct*100,100)+'%';
  document.getElementById('prog-carb').style.width=Math.min(t.carbs/300*100,100)+'%';
  document.getElementById('prog-fat').style.width=Math.min(t.fat/100*100,100)+'%';
  document.getElementById('prog-cal-n').textContent=Math.round(t.kcal)+' / '+Math.round(g.kcal);
  document.getElementById('prog-pro-n').textContent=Math.round(t.protein)+'g / '+Math.round(g.protein)+'g';
  document.getElementById('prog-carb-n').textContent=Math.round(t.carbs)+'g';
  document.getElementById('prog-fat-n').textContent=Math.round(t.fat)+'g';

  const box=document.getElementById('sugg-box');
  const title=document.getElementById('sugg-title');
  const text=document.getElementById('sugg-text');
  const remP=Math.round(g.protein-t.protein);
  if(remP>0){
    box.className='suggestion';
    title.className='suggestion-title orange';
    title.textContent='Need '+remP+'g more protein';
    const tops=getTopProtein();
    text.textContent='Consider adding: '+tops.slice(0,3).join(', ');
  } else {
    box.className='suggestion success';
    title.className='suggestion-title green';
    title.textContent='Protein goal reached';
    text.textContent='Great work today! All macros are on track.';
  }

  // Today log table
  const tbody=document.getElementById('today-log-body');
  const empty=document.getElementById('today-log-empty');
  const todayEntries=mealLog.filter(e=>e.date===today());
  tbody.innerHTML='';
  if(todayEntries.length===0){
    empty.style.display='block';
  } else {
    empty.style.display='none';
    todayEntries.forEach((e,i)=>{
      const tr=document.createElement('tr');
      tr.innerHTML=`<td>${e.name}</td><td><span class="meal-badge ${e.meal}">${e.meal}</span></td><td>${Math.round(e.kcal)}</td><td>${Math.round(e.protein)}</td><td>${Math.round(e.carbs)}</td><td>${Math.round(e.fat)}</td>`;
      tbody.appendChild(tr);
    });
  }
}

function getTopProtein(){
  const items=[];
  for(const m in db){for(const n in db[m]){const f=db[m][n];if(f.protein>3)items.push([n,f.protein/f.serving]);}}
  items.sort((a,b)=>b[1]-a[1]);
  return items.map(x=>x[0]);
}

function deleteLastMeal(){
  const today_str=today();
  let idx=-1;
  for(let i=mealLog.length-1;i>=0;i--){if(mealLog[i].date===today_str){idx=i;break;}}
  if(idx===-1){toast('No meals logged today','red');return;}
  const removed=mealLog[idx];
  mealLog.splice(idx,1);
  saveAll();
  refreshDash();
  toast('Removed: '+removed.name,'red');
}

function clearToday(){
  const t=today();
  mealLog=mealLog.filter(e=>e.date!==t);
  saveAll();
  refreshDash();
  toast('Today\'s meals cleared','red');
}

function updateWater(delta){
  const t = today();
  const current = waterLog[t] || 0;
  const next = Math.max(0, current + delta);
  waterLog[t] = next;
  saveAll();
  refreshDash();
}

// ── LOG MEAL FROM DB ──────────────────────────────────────
function autoMealType(){
  const h=new Date().getHours();
  if(h<12)return'morning';if(h<17)return'lunch';if(h<20)return'evening';return'dinner';
}

function renderLogForm(){
  const meal=document.getElementById('log-meal-type').value;
  const foods=db[meal]||{};
  const container=document.getElementById('log-form-items');
  container.innerHTML='';
  const names=Object.keys(foods);
  if(names.length===0){
    container.innerHTML='<div class="empty"><div class="empty-text">No foods in this category</div></div>';
    return;
  }
  names.forEach(name=>{
    const f=foods[name];
    const unit=f.serving===1?'unit':(f.serving<=10?'units':'g/ml');
    const div=document.createElement('div');
    div.className='food-row';
    div.innerHTML=`
      <div class="food-info">
        <div class="food-name">${name}</div>
        <div class="food-macro">${f.kcal}kcal · ${f.protein}g P · ${f.carbs}g C · ${f.fat}g F per ${f.serving}${unit}</div>
      </div>
      <div class="food-qty">
        <input class="qty-input" type="number" min="0" step="${f.serving===1?1:10}" placeholder="0" id="qty_${name.replace(/\s+/g,'_')}" oninput="updateLogPreview()">
        <span class="qty-unit">${unit}</span>
      </div>
    `;
    container.appendChild(div);
  });
}

function updateLogPreview(){
  const meal=document.getElementById('log-meal-type').value;
  const foods=db[meal]||{};
  let cal=0,pro=0,carb=0,fat=0;
  for(const name in foods){
    const el=document.getElementById('qty_'+name.replace(/\s+/g,'_'));
    if(!el)continue;
    const qty=parseFloat(el.value)||0;
    if(qty>0){
      const f=foods[name];
      const fc=qty/f.serving;
      cal+=f.kcal*fc;pro+=f.protein*fc;carb+=f.carbs*fc;fat+=f.fat*fc;
    }
  }
  document.getElementById('prev-cal').textContent=Math.round(cal);
  document.getElementById('prev-pro').textContent=Math.round(pro);
  document.getElementById('prev-carb').textContent=Math.round(carb);
  document.getElementById('prev-fat').textContent=Math.round(fat);
  updateSplitBar('spl-p','spl-c','spl-f',pro,carb,fat);
}

function updateSplitBar(pid,cid,fid,p,c,f){
  const total=p+c+f||1;
  document.getElementById(pid).style.width=(p/total*100)+'%';
  document.getElementById(cid).style.width=(c/total*100)+'%';
  document.getElementById(fid).style.width=(f/total*100)+'%';
}

function saveLogMeal(){
  const meal=document.getElementById('log-meal-type').value;
  const foods=db[meal]||{};
  let cal=0,pro=0,carb=0,fat=0;
  const parts=[];
  for(const name in foods){
    const el=document.getElementById('qty_'+name.replace(/\s+/g,'_'));
    if(!el)continue;
    const qty=parseFloat(el.value)||0;
    if(qty>0){
      const f=foods[name];
      const fc=qty/f.serving;
      cal+=f.kcal*fc;pro+=f.protein*fc;carb+=f.carbs*fc;fat+=f.fat*fc;
      parts.push(name);
    }
  }
  if(cal===0&&pro===0){toast('Enter at least one quantity','red');return;}
  mealLog.push({date:today(),meal,name:parts.join(', '),kcal:cal,protein:pro,carbs:carb,fat:fat,type:'db'});
  saveAll();
  toast('Meal logged — '+Math.round(cal)+' kcal, '+Math.round(pro)+'g protein');
  renderLogForm();
  refreshDash();
}

// ── QUICK ADD (manual entry) ──────────────────────────────
async function fetchNutrients(){
  const name=document.getElementById('ca-name').value.trim();
  const weight=parseFloat(document.getElementById('ca-weight').value)||100;
  if(!name){toast('Please enter a food name first','red');return;}
  
  const btn=document.getElementById('ca-btn-fetch');
  btn.textContent='Fetching...';
  btn.disabled=true;
  
  // 1. Check local DB first
  const lowerName = name.toLowerCase();
  let localFood = null;
  for(const cat in db) {
    if(db[cat][lowerName]) {
      localFood = db[cat][lowerName];
      break;
    }
  }

  if (localFood) {
    const unitType = document.getElementById('ca-unit').value;
    let factor = weight / localFood.serving; 
    
    if (unitType === 'g' && localFood.serving <= 10) {
      factor = weight / 50; // Assume 1 unit = 50g for things like eggs/bananas
    } else if (unitType === 'unit' && localFood.serving >= 50) {
      factor = weight; // e.g. 2 units of 100g chicken = 2 * 100g = factor of 2
    }

    document.getElementById('ca-kcal').value = Math.round(localFood.kcal * factor);
    document.getElementById('ca-pro').value = Math.round(localFood.protein * factor * 10) / 10;
    document.getElementById('ca-carbs').value = Math.round(localFood.carbs * factor * 10) / 10;
    document.getElementById('ca-fat').value = Math.round(localFood.fat * factor * 10) / 10;
    
    updateCustomPreview();
    toast('Calculated from your local Food Database!');
    btn.textContent='Auto-Calculate';
    btn.disabled=false;
    return;
  }
  
  // 2. Fallback to Open Food Facts API
  try{
    const targetUrl = `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(name)}&search_simple=1&action=process&json=1&page_size=1`;
    const url = `https://corsproxy.io/?${encodeURIComponent(targetUrl)}`;
    const res = await fetch(url);
    const data = await res.json();
    
    if(data.products && data.products.length > 0){
      const p = data.products[0];
      const nut = p.nutriments || {};
      
      const unitType = document.getElementById('ca-unit').value;
      let factor = weight / 100;
      if (unitType === 'unit') {
        const serving = parseFloat(p.serving_quantity);
        if (!isNaN(serving) && serving > 0) {
          factor = (weight * serving) / 100;
        } else {
          toast('Serving size unknown. Treating 1 unit as 100g', 'red');
          factor = weight; 
        }
      }
      
      const kcal = (nut['energy-kcal_100g'] || 0) * factor;
      const pro = (nut['proteins_100g'] || 0) * factor;
      const carb = (nut['carbohydrates_100g'] || 0) * factor;
      const fat = (nut['fat_100g'] || 0) * factor;
      
      document.getElementById('ca-kcal').value = Math.round(kcal);
      document.getElementById('ca-pro').value = Math.round(pro * 10) / 10;
      document.getElementById('ca-carbs').value = Math.round(carb * 10) / 10;
      document.getElementById('ca-fat').value = Math.round(fat * 10) / 10;
      
      updateCustomPreview();
      toast('Nutrients fetched for ' + (p.product_name || name));
    } else {
      toast('Food not found in database','red');
    }
  } catch(e) {
    console.error(e);
    toast('Error fetching data','red');
  }
  
  btn.textContent='Auto-Calculate';
  btn.disabled=false;
}

function updateCustomPreview(){
  const kcal=parseFloat(document.getElementById('ca-kcal').value)||0;
  const pro=parseFloat(document.getElementById('ca-pro').value)||0;
  const carb=parseFloat(document.getElementById('ca-carbs').value)||0;
  const fat=parseFloat(document.getElementById('ca-fat').value)||0;
  const name=document.getElementById('ca-name').value.trim()||'—';
  const meal=document.getElementById('ca-meal').value;
  document.getElementById('ca-preview-name').textContent=name;
  document.getElementById('ca-preview-meal').textContent='Meal: '+meal;
  document.getElementById('ca-prev-cal').textContent=Math.round(kcal);
  document.getElementById('ca-prev-pro').textContent=Math.round(pro);
  document.getElementById('ca-prev-carb').textContent=Math.round(carb);
  document.getElementById('ca-prev-fat2').textContent=Math.round(fat);
  updateSplitBar('ca-spl-p','ca-spl-c','ca-spl-f',pro,carb,fat);
}

function renderCustomRemaining(){
  const t=todayTotals();
  const g=getGoals();
  const box=document.getElementById('ca-remaining');
  const remCal=Math.round(g.kcal-t.kcal);
  const remPro=Math.round(g.protein-t.protein);
  box.innerHTML=`
    <div style="display:flex;gap:8px">
      <div class="macro-chip"><div class="macro-chip-val" style="color:var(--orange);font-size:14px">${remCal}</div><div class="macro-chip-lbl">cal left</div></div>
      <div class="macro-chip"><div class="macro-chip-val" style="color:var(--green);font-size:14px">${remPro}</div><div class="macro-chip-lbl">protein left</div></div>
    </div>
  `;
}

function saveCustomMeal(){
  const name=document.getElementById('ca-name').value.trim();
  const meal=document.getElementById('ca-meal').value;
  const kcal=parseFloat(document.getElementById('ca-kcal').value)||0;
  const pro=parseFloat(document.getElementById('ca-pro').value)||0;
  const carb=parseFloat(document.getElementById('ca-carbs').value)||0;
  const fat=parseFloat(document.getElementById('ca-fat').value)||0;
  if(!name){toast('Enter a food name','red');return;}
  if(kcal===0&&pro===0&&carb===0&&fat===0){toast('Enter at least one macro value','red');return;}
  mealLog.push({date:today(),meal,name,kcal,protein:pro,carbs:carb,fat,type:'custom'});
  if(document.getElementById('ca-save-db').checked){
    const key=name.toLowerCase();
    if(!db[meal])db[meal]={};
    db[meal][key]={serving:100,kcal,protein:pro,carbs:carb,fat};
    toast('Logged & saved to database!');
  } else {
    toast('Logged: '+name+' — '+Math.round(kcal)+' kcal');
  }
  saveAll();
  document.getElementById('ca-name').value='';
  document.getElementById('ca-weight').value='';
  document.getElementById('ca-kcal').value='';
  document.getElementById('ca-pro').value='';
  document.getElementById('ca-carbs').value='';
  document.getElementById('ca-fat').value='';
  document.getElementById('ca-save-db').checked=false;
  updateCustomPreview();
  renderCustomRemaining();
  refreshDash();
}

// ── TRENDS ────────────────────────────────────────────────
function renderTrends(){
  renderWeightChart();
  renderCalorieChart();
}

function renderWeightChart(){
  const canvas = document.getElementById('wt-canvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const empty = document.getElementById('wt-empty');
  if(weightLog.length === 0){
    canvas.style.display = 'none';
    empty.style.display = 'block';
    return;
  }
  canvas.style.display = 'block';
  empty.style.display = 'none';
  const data = [...weightLog].sort((a,b)=>a.date.localeCompare(b.date)).slice(-14);
  const w = canvas.width = canvas.offsetWidth;
  const h = canvas.height = canvas.offsetHeight;
  ctx.clearRect(0,0,w,h);
  const maxW = Math.max(...data.map(d=>d.weight)) + 2;
  const minW = Math.max(0, Math.min(...data.map(d=>d.weight)) - 2);
  ctx.beginPath();
  ctx.strokeStyle = '#8b5cf6';
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  const stepX = w / Math.max(1, (data.length - 1));
  data.forEach((d, i) => {
    const x = i * stepX;
    const y = h - ((d.weight - minW) / (maxW - minW) * h);
    if(i===0) ctx.moveTo(x,y);
    else ctx.lineTo(x,y);
  });
  ctx.stroke();
  ctx.fillStyle = '#8b5cf6';
  data.forEach((d, i) => {
    const x = i * stepX;
    const y = h - ((d.weight - minW) / (maxW - minW) * h);
    ctx.beginPath();
    ctx.arc(x,y,4,0,Math.PI*2);
    ctx.fill();
    ctx.fillStyle = 'white';
    ctx.font = '10px sans-serif';
    ctx.fillText(d.weight, x-6, y-8);
    ctx.fillStyle = '#8b5cf6';
  });
}

function renderCalorieChart(){
  const canvas = document.getElementById('cal-canvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const empty = document.getElementById('cal-empty');
  const dates = [];
  for(let i=13; i>=0; i--){
    const d = new Date();
    d.setDate(d.getDate() - i);
    dates.push(d.toISOString().slice(0,10));
  }
  const data = dates.map(date => {
    const entries = mealLog.filter(e=>e.date===date);
    let kcal = 0;
    entries.forEach(e=>kcal+=e.kcal);
    return {date, kcal};
  });
  if(data.every(d=>d.kcal===0)){
    canvas.style.display = 'none';
    empty.style.display = 'block';
    return;
  }
  canvas.style.display = 'block';
  empty.style.display = 'none';
  const w = canvas.width = canvas.offsetWidth;
  const h = canvas.height = canvas.offsetHeight;
  ctx.clearRect(0,0,w,h);
  const maxK = Math.max(1000, ...data.map(d=>d.kcal)) * 1.1;
  const barW = (w / 14) * 0.6;
  const stepX = w / 14;
  data.forEach((d, i) => {
    const x = i * stepX + (stepX - barW)/2;
    const barH = (d.kcal / maxK) * h;
    const y = h - barH;
    const grd = ctx.createLinearGradient(0, y, 0, h);
    grd.addColorStop(0, '#f59e0b');
    grd.addColorStop(1, 'rgba(245, 158, 11, 0.2)');
    ctx.fillStyle = grd;
    ctx.beginPath();
    ctx.moveTo(x, h);
    ctx.lineTo(x, y + 4);
    ctx.quadraticCurveTo(x, y, x + 4, y);
    ctx.lineTo(x + barW - 4, y);
    ctx.quadraticCurveTo(x + barW, y, x + barW, y + 4);
    ctx.lineTo(x + barW, h);
    ctx.fill();
  });
}

function saveWeight(){
  const el = document.getElementById('wt-input');
  const w = parseFloat(el.value);
  if(isNaN(w) || w<10 || w>300) { toast('Invalid weight','red'); return; }
  const t = today();
  weightLog = weightLog.filter(x => x.date !== t);
  weightLog.push({date:t, weight:w});
  saveAll();
  el.value='';
  toast('Weight saved: '+w+'kg');
  renderTrends();
}

// ── FOOD DB ───────────────────────────────────────────────
let curDBTab='morning';
function switchDBTab(cat,el){
  curDBTab=cat;
  document.querySelectorAll('#db-tabs .tab').forEach(t=>t.classList.remove('active'));
  if(el)el.classList.add('active');
  renderDBList(cat);
}

function renderDBList(cat){
  const foods=db[cat]||{};
  const list=document.getElementById('db-list');
  const names=Object.keys(foods);
  if(names.length===0){list.innerHTML='<div class="empty"><div class="empty-text">No foods added yet</div></div>';return;}
  list.innerHTML='';
  names.forEach(name=>{
    const f=foods[name];
    const row=document.createElement('div');
    row.className='food-row';
    row.innerHTML=`
      <div class="food-info">
        <div class="food-name">${name}</div>
        <div class="food-macro">per ${f.serving}g/unit — ${f.kcal}kcal · ${f.protein}g P · ${f.carbs}g C · ${f.fat}g F</div>
      </div>
      <button class="btn btn-danger btn-sm" onclick="deleteFood('${cat}','${name}')">Remove</button>
    `;
    list.appendChild(row);
  });
}

function saveFoodDB(){
  const meal=document.getElementById('db-meal').value;
  const name=document.getElementById('db-name').value.trim().toLowerCase();
  const srv=parseFloat(document.getElementById('db-serving').value)||100;
  const kcal=parseFloat(document.getElementById('db-kcal').value)||0;
  const pro=parseFloat(document.getElementById('db-pro').value)||0;
  const carbs=parseFloat(document.getElementById('db-carbs').value)||0;
  const fat=parseFloat(document.getElementById('db-fat').value)||0;
  if(!name){toast('Enter a food name','red');return;}
  if(!db[meal])db[meal]={};
  db[meal][name]={serving:srv,kcal,protein:pro,carbs,fat};
  saveAll();
  toast('Added: '+name);
  ['db-name','db-serving','db-kcal','db-pro','db-carbs','db-fat'].forEach(id=>document.getElementById(id).value='');
  if(curDBTab===meal)renderDBList(meal);
}

function deleteFood(cat,name){
  delete db[cat][name];
  saveAll();
  renderDBList(cat);
  toast('Removed: '+name,'red');
}

// ── SETTINGS ──────────────────────────────────────────────
function initSettings(){
  document.getElementById('set-kcal').value=settings.goal_kcal;
  document.getElementById('set-pro').value=settings.goal_protein;
  document.getElementById('account-name').textContent = 'Logged in as ' + nf_username;
  syncBulkUI();
}

function saveSettings(){
  const k=parseFloat(document.getElementById('set-kcal').value);
  const p=parseFloat(document.getElementById('set-pro').value);
  if(isNaN(k)||isNaN(p)||k<500||p<10){toast('Invalid values','red');return;}
  settings.goal_kcal=k;settings.goal_protein=p;
  saveAll();
  refreshDash();
  toast('Settings saved');
}

function toggleChatSidebar() {
  document.getElementById('chat-sidebar').classList.toggle('collapsed');
}

function renderChatSidebar() {
  const list = document.getElementById('session-list');
  list.innerHTML = '';
  chatSessions.forEach(s => {
    const div = document.createElement('div');
    div.className = 'session-item' + (s.id === currentSessionId ? ' active' : '');
    div.textContent = s.title;
    div.onclick = () => loadSession(s.id);
    list.appendChild(div);
  });
}

function loadSession(id) {
  currentSessionId = id;
  renderChatSidebar();
  renderChatHistory();
}

function newSession() {
  const id = Date.now();
  chatSessions.unshift({ id, title: 'New Chat', messages: [] });
  currentSessionId = id;
  saveAll();
  renderChatSidebar();
  renderChatHistory();
}

function renderChatHistory() {
  const history = document.getElementById('chat-history');
  const session = chatSessions.find(s => s.id === currentSessionId);
  if (!session || !session.messages || session.messages.length === 0) {
    history.innerHTML = `
      <div class="gemini-greeting">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L14.5 10.5L23 13L14.5 15.5L12 24L9.5 15.5L1 13L9.5 10.5L12 2Z" fill="url(#grad)" />
          <defs>
            <linearGradient id="grad" x1="1" y1="2" x2="23" y2="24" gradientUnits="userSpaceOnUse">
              <stop stop-color="#6366f1"/>
              <stop offset="0.5" stop-color="#a855f7"/>
              <stop offset="1" stop-color="#ec4899"/>
            </linearGradient>
          </defs>
        </svg>
        <h1>Hi ${nf_username || 'there'},<br>What's on your mind?</h1>
      </div>
    `;
    return;
  }

  history.innerHTML = '';
  session.messages.forEach(msg => {
    const div = document.createElement('div');
    div.className = msg.role === 'user' ? 'chat-msg user' : 'chat-msg ai';
    div.textContent = msg.parts[0].text;
    history.appendChild(div);
  });
  history.scrollTop = history.scrollHeight;
}

function clearChat() {
  const session = chatSessions.find(s => s.id === currentSessionId);
  if(session) session.messages = [];
  saveAll();
  renderChatHistory();
}

async function sendChat(){
  const input = document.getElementById('chat-input-field');
  const text = input.value.trim();
  if(!text) return;
  if(!(import.meta.env.VITE_GEMINI_API_KEY || settings.gemini_key)){ toast('Please add Gemini API key in Settings','red'); return; }
  
  const session = chatSessions.find(s => s.id === currentSessionId);
  if (!session) return;
  
  if (session.messages.length === 0) {
    session.title = text.substring(0, 30) + (text.length > 30 ? '...' : '');
    renderChatSidebar();
  }
  
  session.messages.push({ role: 'user', parts: [{ text }] });
  saveAll();
  renderChatHistory();
  input.value = '';
  
  const historyEl = document.getElementById('chat-history');
  const aiDiv = document.createElement('div');
  aiDiv.className = 'chat-msg ai';
  aiDiv.textContent = '';
  const loadIndicator = document.createElement('span');
  loadIndicator.innerHTML = '<span class="typing-dot" style="display:inline-block;margin-left:4px"></span><span class="typing-dot" style="display:inline-block;margin-left:2px"></span><span class="typing-dot" style="display:inline-block;margin-left:2px"></span>';
  aiDiv.appendChild(loadIndicator);
  historyEl.appendChild(aiDiv);
  historyEl.scrollTop = historyEl.scrollHeight;
  
  try {
    const t = todayTotals();
    const g = getGoals();
    const w = weightLog.length > 0 ? weightLog[weightLog.length-1].weight : 'unknown';
    
    const sysPrompt = `You are an expert AI nutritionist and health coach named 'NutriFit AI'. The user's name is ${nf_username || 'User'}. Their daily goal is ${Math.round(g.kcal)} kcal and ${Math.round(g.protein)}g protein. Today they have consumed ${Math.round(t.kcal)} kcal and ${Math.round(t.protein)}g protein. Their current weight is ${w} kg. Be concise, encouraging, and helpful. Format your responses as plain text with short paragraphs. IMPORTANT: If the user tells you they ate or drank something, you MUST auto-log it for them by outputting this exact tag at the very end of your response: [LOG_MEAL: Food Name | kcal | protein | carbs | fat | mealType] (mealType must be breakfast, lunch, dinner, or snack). For example: [LOG_MEAL: 2 Eggs | 140 | 12 | 1 | 10 | breakfast]. If you don't know the exact macros, estimate them. If they ate multiple things, output multiple tags.`;
    
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:streamGenerateContent?alt=sse&key=${(import.meta.env.VITE_GEMINI_API_KEY || settings.gemini_key)}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        system_instruction: { parts: { text: sysPrompt } },
        contents: session.messages
      })
    });
    
    if(!res.ok){
      const errData = await res.json();
      throw new Error(errData.error?.message || 'API Error');
    }
    
    aiDiv.removeChild(loadIndicator);
    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let fullResponse = '';
    
    while(true) {
      const {done, value} = await reader.read();
      if(done) break;
      const chunk = decoder.decode(value, {stream: true});
      const lines = chunk.split('\n');
      for(const line of lines) {
        if(line.startsWith('data: ')) {
          const dataStr = line.replace('data: ', '').trim();
          if(dataStr) {
            try {
              const data = JSON.parse(dataStr);
              if(data.candidates && data.candidates[0].content.parts[0].text) {
                fullResponse += data.candidates[0].content.parts[0].text;
                let displayResponse = fullResponse.replace(/\[LOG_MEAL:.*?\]/gi, '').trim();
                aiDiv.textContent = displayResponse;
                historyEl.scrollTop = historyEl.scrollHeight;
              }
            } catch(e) {}
          }
        }
      }
    }
    
    const regex = /\[LOG_MEAL:\s*(.*?)\s*\|\s*(\d+\.?\d*)\s*\|\s*(\d+\.?\d*)\s*\|\s*(\d+\.?\d*)\s*\|\s*(\d+\.?\d*)\s*\|\s*([a-z]+)\s*\]/gi;
    let match;
    let numLogged = 0;
    while((match = regex.exec(fullResponse)) !== null) {
      const [, mName, mKcal, mPro, mCarb, mFat, mType] = match;
      mealLog.push({
        date: today(),
        meal: mType.toLowerCase(),
        name: mName.trim(),
        kcal: parseFloat(mKcal),
        protein: parseFloat(mPro),
        carbs: parseFloat(mCarb),
        fat: parseFloat(mFat),
        type: 'custom'
      });
      numLogged++;
    }
    
    if (numLogged > 0) {
      toast(`Successfully auto-logged ${numLogged} item(s)!`, 'green');
      if (typeof syncBulkUI === 'function') syncBulkUI();
      if (typeof refreshDash === 'function') refreshDash();
      if (typeof renderLogForm === 'function') renderLogForm();
    }
    
    const cleanResponse = fullResponse.replace(/\[LOG_MEAL:.*?\]/gi, '').trim();
    aiDiv.textContent = cleanResponse;
    session.messages.push({ role: 'model', parts: [{ text: cleanResponse }] });
    saveAll();
    
  } catch(err){
    aiDiv.textContent = 'Error: ' + err.message;
    session.messages.pop();
    saveAll();
    toast('Failed to reach AI Coach', 'red');
  }
}

// ── INIT ──────────────────────────────────────────────────
document.getElementById('page-date').textContent=new Date().toLocaleDateString('en-IN',{weekday:'long',day:'numeric',month:'long'});
renderChatSidebar();
renderChatHistory();
document.getElementById('log-meal-type').value=autoMealType();
refreshDash();
renderLogForm();
renderCustomRemaining();

// pre-populate weight log from bundled CSV data
if(weightLog.length===0){
  const csvWeights=[
    {date:'2026-03-21',weight:55},{date:'2026-03-22',weight:55},{date:'2026-03-23',weight:53},
    {date:'2026-03-24',weight:55},{date:'2026-03-25',weight:55},{date:'2026-03-26',weight:58},
    {date:'2026-03-27',weight:55},{date:'2026-03-28',weight:59},{date:'2026-03-29',weight:55},
    {date:'2026-03-30',weight:55}
  ];
  weightLog=csvWeights;
}

// ── CLOUD SYNC LOGIC ──────────────────────────────────────
window.syncToCloud = null;

import { initializeApp } from "firebase/app";
  import { getFirestore, doc, getDoc, setDoc, onSnapshot } from "firebase/firestore";

  const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    measurementId: "G-226D7JHKSF"
  };

  let app, firestore;
  try {
    if (firebaseConfig.apiKey) {
      app = initializeApp(firebaseConfig);
      firestore = getFirestore(app);
    } else {
      console.warn("Firebase API key missing. Running in local-only mode.");
    }
  } catch (e) {
    console.error("Firebase init error", e);
  }

  let unsubscribe = null;
  let isRemoteUpdate = false;
  let authMode = 'login';

  window.switchAuth = function(mode) {
    authMode = mode;
    document.getElementById('tab-login').className = 'a-tab ' + (mode==='login'?'active':'');
    document.getElementById('tab-signup').className = 'a-tab ' + (mode==='signup'?'active':'');
    document.getElementById('f-name').style.display = mode==='signup' ? 'block' : 'none';
    document.getElementById('btn-auth').textContent = mode==='signup' ? 'Sign Up' : 'Log In';
  };

  window.logout = function() {
    localStorage.removeItem('nf_username');
    location.reload();
  };

  window.handleAuth = async function() {
    const un = document.getElementById('auth-user').value.trim().toLowerCase();
    const pw = document.getElementById('auth-pass').value.trim();
    const nm = document.getElementById('auth-name').value.trim();
    
    if(!un || !pw) { toast('Please fill username and password', 'red'); return; }
    if (!firestore) { toast('Cloud sync is unavailable. Check Vercel environment variables.', 'red'); return; }
    
    const userRef = doc(firestore, 'accounts', un);
    const btn = document.getElementById('btn-auth');
    btn.textContent = 'Processing...';
    btn.disabled = true;

    try {
      const snap = await getDoc(userRef);
      if(authMode === 'login') {
        if(!snap.exists()) { toast('Username not found', 'red'); }
        else if(snap.data().password !== pw) { toast('Incorrect password', 'red'); }
        else { finishAuth(un); }
      } else {
        if(snap.exists()) { toast('Username already taken', 'red'); }
        else if(!nm) { toast('Please enter your full name', 'red'); }
        else { await setDoc(userRef, { name: nm, password: pw, createdAt: new Date() }); finishAuth(un); }
      }
    } catch(err) {
      console.error(err);
      toast('Network error occurred', 'red');
    }
    btn.textContent = authMode === 'signup' ? 'Sign Up' : 'Log In';
    btn.disabled = false;
  };

  function finishAuth(un) {
    nf_username = un;
    localStorage.setItem('nf_username', un);
    document.getElementById('auth-overlay').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    toast('Logged in successfully!');
    if(document.getElementById('page-settings').classList.contains('active')) initSettings();
    connectCloud();
  }

  function connectCloud() {
    if(!nf_username) return;
    if(!firestore) return;
    if(unsubscribe) unsubscribe();
    
    const docRef = doc(firestore, 'users', nf_username);
    
    // Setup write function for saveAll
    window.syncToCloud = async () => {
      if(isRemoteUpdate) return;
      try {
        await setDoc(docRef, { db, settings, mealLog, weightLog, waterLog, chatSessions });
      } catch (err) {
        console.error('Firebase DB Save error', err);
      }
    };

    let firstLoad = true;

    // Listen for remote updates
    unsubscribe = onSnapshot(docRef, (docSnap) => {
      if (!docSnap.exists() && firstLoad) {
        // Document doesn't exist on cloud, push local data (default setup)
        window.syncToCloud();
      } else if (docSnap.exists() && !docSnap.metadata.hasPendingWrites) {
        const data = docSnap.data();
        if(data) {
          isRemoteUpdate = true;
          if(data.db) db = data.db;
          if(data.settings) settings = data.settings;
          if(data.mealLog) mealLog = data.mealLog;
          if(data.weightLog) weightLog = data.weightLog;
          if(data.waterLog) waterLog = data.waterLog;
          if(data.chatSessions) chatSessions = data.chatSessions;
          
          LSset('nf_db',db);
          LSset('nf_settings',settings);
          LSset('nf_log',mealLog);
          LSset('nf_weight',weightLog);
          LSset('nf_water',waterLog);
          LSset('nf_sessions',chatSessions);
          
          syncBulkUI();
          refreshDash();
          renderLogForm();
          if(document.getElementById('page-weight').classList.contains('active')) renderTrends();
          if(document.getElementById('page-custom').classList.contains('active')) renderCustomRemaining();
          if(document.getElementById('page-settings').classList.contains('active')) initSettings();
          if(document.getElementById('page-foods').classList.contains('active')) renderDBList(curDBTab);
          
          isRemoteUpdate = false;
        }
      }
      firstLoad = false;
    }, (error) => {
      console.error("Firestore Listen error", error);
    });
  }

  // Auto connect if logged in
  if(nf_username) {
    document.getElementById('auth-overlay').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    connectCloud();
  } else {
    document.getElementById('auth-overlay').style.display = 'flex';
    document.getElementById('app').style.display = 'none';
  }


// Expose functions to window for inline HTML handlers
window.LS = LS;
window.LSset = LSset;
window.saveAll = saveAll;
window.today = today;
window.getGoals = getGoals;
window.todayTotals = todayTotals;
window.toast = toast;
window.gotoPage = gotoPage;
window.toggleBulk = toggleBulk;
window.syncBulkUI = syncBulkUI;
window.applyTheme = applyTheme;
window.toggleTheme = toggleTheme;
window.setRing = setRing;
window.refreshDash = refreshDash;
window.getTopProtein = getTopProtein;
window.deleteLastMeal = deleteLastMeal;
window.clearToday = clearToday;
window.updateWater = updateWater;
window.autoMealType = autoMealType;
window.renderLogForm = renderLogForm;
window.updateLogPreview = updateLogPreview;
window.updateSplitBar = updateSplitBar;
window.saveLogMeal = saveLogMeal;
window.fetchNutrients = fetchNutrients;
window.updateCustomPreview = updateCustomPreview;
window.renderCustomRemaining = renderCustomRemaining;
window.saveCustomMeal = saveCustomMeal;
window.renderTrends = renderTrends;
window.renderWeightChart = renderWeightChart;
window.renderCalorieChart = renderCalorieChart;
window.saveWeight = saveWeight;
window.switchDBTab = switchDBTab;
window.renderDBList = renderDBList;
window.saveFoodDB = saveFoodDB;
window.deleteFood = deleteFood;
window.initSettings = initSettings;
window.saveSettings = saveSettings;
window.sendChat = sendChat;
window.finishAuth = finishAuth;
window.connectCloud = connectCloud;
window.newSession = newSession;
window.switchSession = switchSession;
window.deleteSession = deleteSession;
window.toggleChatSidebar = toggleChatSidebar;
window.clearChat = clearChat;
