const $ = id => document.getElementById(id);
let activeCase = null, selectedPuzzle = null, selectedSuspect = null, toastTimer;
async function api(url, method="GET", body=null) {
  const options = {method, headers: {"Content-Type":"application/json"}};
  if (body !== null) options.body = JSON.stringify(body);
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong");
  return data;
}
function notify(message) {
  $("toast").textContent = message; $("toast").classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(()=>$("toast").classList.remove("show"), 2600);
}
function show(view) {
  ["home","game","historyView"].forEach(v => $(v).classList.toggle("hidden", v !== view));
  window.scrollTo({top:0,behavior:"smooth"});
}
async function init() {
  try { const s=await api("/api/status"); $("mode").textContent=s.mode; }
  catch(e){ $("mode").textContent="Offline"; }
  await loadCases();
}
async function loadCases() {
  const cases=await api("/api/cases");
  $("caseGrid").innerHTML=cases.map(c=>`
    <article class="case-card"><div class="case-icon">✧</div><div class="tags"><span class="tag">${c.category}</span><span class="tag">${c.difficulty}</span></div>
    <h3>${esc(c.title)}</h3><p>${esc(c.story)}</p><small class="muted">⌖ ${esc(c.location)}</small>
    <button class="btn btn-gold" style="margin-top:16px" onclick="startCase('${c.id}')">Open case file →</button></article>`).join("");
}
function esc(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
async function startCase(id) {
  try { await api("/api/start","POST",{case_id:id}); activeCase=await api("/api/case"); selectedPuzzle=null;selectedSuspect=null;renderCase();show("game"); }
  catch(e){notify(e.message);}
}
function renderCase() {
  $("caseTitle").textContent=activeCase.title;$("score").textContent=activeCase.score;
  $("meta").innerHTML=`<span class="tag">${esc(activeCase.category)}</span><span class="tag">${esc(activeCase.difficulty)}</span><span class="tag">${esc(activeCase.location)}</span>`;
  $("story").textContent=activeCase.story;
  $("suspects").innerHTML=activeCase.suspects.map(s=>`<article class="suspect"><h4>${esc(s.name)}</h4><div class="role">${esc(s.role)}</div><p><strong>Background:</strong> ${esc(s.background)}</p><p><strong>Motive:</strong> ${esc(s.motive)}</p><p><strong>Alibi:</strong> ${esc(s.alibi)}</p></article>`).join("");
  $("evidence").innerHTML=activeCase.evidence.map(e=>`<article class="evidence-card"><h4>⌕ ${esc(e.title)}</h4><p>${esc(e.description)}</p><button class="btn btn-outline" id="collect-${e.id}" onclick="collectEvidence('${e.id}')">Collect clue</button></article>`).join("");
  $("puzzleQuestion").textContent=activeCase.puzzle.question;
  $("puzzleOptions").innerHTML=activeCase.puzzle.options.map((o,i)=>`<button class="option" onclick="selectPuzzle(this,${i})">${esc(o)}</button>`).join("");
  $("accuseOptions").innerHTML=activeCase.suspects.map((s,i)=>`<button class="option" onclick="selectSuspect(this,${i})">${esc(s.name)} — ${esc(s.role)}</button>`).join("");
  updateBoard();$("puzzleFeedback").textContent="";$("hintText").textContent="";$("result").classList.add("hidden");
  $("chatLog").innerHTML='<div class="bubble bot">Good day, detective. Ask me to help connect the clues or examine an alibi.</div>';
}
function selectPuzzle(el,i){document.querySelectorAll("#puzzleOptions .option").forEach(x=>x.classList.remove("selected"));el.classList.add("selected");selectedPuzzle=activeCase.puzzle.options[i];}
function selectSuspect(el,i){document.querySelectorAll("#accuseOptions .option").forEach(x=>x.classList.remove("selected"));el.classList.add("selected");selectedSuspect=activeCase.suspects[i].name;}
async function collectEvidence(id){
  try{const r=await api(`/api/evidence/${id}`,"POST",{});activeCase=await api("/api/case");$("score").textContent=r.score;updateBoard();const b=$(`collect-${id}`);if(b)b.disabled=true;notify(r.message);}
  catch(e){notify(e.message);}
}
function updateBoard(){
  const items=activeCase.evidence.filter(e=>activeCase.collected.includes(e.id));
  $("evidenceCount").textContent=items.length;
  $("board").innerHTML=items.length?items.map(e=>`<div class="board-item"><b>${esc(e.title)}</b>${esc(e.description)}</div>`).join(""):'<p class="muted">Your collected clues will appear here.</p>';
  activeCase.evidence.forEach(e=>{const b=$(`collect-${e.id}`);if(b)b.disabled=activeCase.collected.includes(e.id);});
}
$("submitPuzzle").onclick=async()=>{
  if(!selectedPuzzle)return notify("Choose an answer first.");
  try{const r=await api("/api/puzzle","POST",{answer:selectedPuzzle});$("puzzleFeedback").textContent=r.message;$("puzzleFeedback").style.color=r.correct?"#72c69b":"#e58d8d";$("score").textContent=r.score;activeCase=await api("/api/case");}
  catch(e){notify(e.message);}
};
$("hintBtn").onclick=async()=>{
  try{const r=await api("/api/hint","POST",{});$("hintText").textContent=r.hint;$("score").textContent=r.score;activeCase=await api("/api/case");}
  catch(e){notify(e.message);}
};
$("chatForm").onsubmit=async e=>{
  e.preventDefault();const input=$("chatInput"),message=input.value.trim();if(!message)return;
  addBubble(message,"user");input.value="";
  try{const r=await api("/api/chat","POST",{message});addBubble(r.reply,"bot");}
  catch(err){addBubble(err.message,"bot");}
};
function addBubble(text,kind){const el=document.createElement("div");el.className=`bubble ${kind}`;el.textContent=text;$("chatLog").appendChild(el);$("chatLog").scrollTop=$("chatLog").scrollHeight;}
$("accuseBtn").onclick=async()=>{
  if(!selectedSuspect)return notify("Select a suspect before accusing.");
  if(!confirm(`Are you sure you want to accuse ${selectedSuspect}?`))return;
  try{const r=await api("/api/accuse","POST",{suspect:selectedSuspect});$("score").textContent=r.score;
    $("result").className="result"+(r.correct?"":" wrong");
    $("result").innerHTML=`<strong>${esc(r.message)}</strong><p>Correct culprit: <b>${esc(r.solution)}</b></p><p>${esc(r.explanation)}</p><p>Final score: <b>${r.score}</b></p><button class="btn btn-gold" onclick="newCase()">Start another case</button>`;
    $("result").classList.remove("hidden");notify(r.correct?"Case solved!":"Case completed.");
  }catch(e){notify(e.message);}
};
$("generateBtn").onclick=async()=>{
  $("generateBtn").disabled=true;$("generateBtn").textContent="Generating…";
  try{const r=await api("/api/generate","POST",{});await loadCases();notify("New AI case added to the archive.");}
  catch(e){notify(e.message);}
  finally{$("generateBtn").disabled=false;$("generateBtn").textContent="✧ Generate AI case";}
};
async function newCase(){await api("/api/new","POST",{});activeCase=null;show("home");await loadCases();}
$("backBtn").onclick=newCase;
$("historyBtn").onclick=showHistory;$("historyBack").onclick=()=>show("home");
async function showHistory(){
  try{const rows=await api("/api/history");$("historyList").innerHTML=rows.length?rows.map(r=>`<div class="history-item"><div><b>${esc(r.title)}</b><br><small>${esc(r.completed_at)} · Accused: ${esc(r.suspect)}</small></div><div><b>${r.correct?"Solved":"Unsolved"}</b><br><small>Score: ${r.score}</small></div></div>`).join(""):'<p class="muted">No completed investigations yet. Solve a case to see it here.</p>';show("historyView");}
  catch(e){notify(e.message);}
}
init();
