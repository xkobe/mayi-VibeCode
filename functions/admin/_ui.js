// 管理后台 UI（单页，内联 CSS/JS，无外链）
export const uiHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>术语台 · 管理后台</title>
<style>
  :root{--bg:#f6f5f2;--card:#fff;--ink:#1f1d1a;--ink2:#6b665d;--line:#e7e2d8;--brand:#C8442E;--brand2:#a8361f;--ok:#2e9e5b;--warn:#d98a00;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);font-size:14px}
  a{color:inherit}
  button{font-family:inherit;cursor:pointer}
  .btn{background:var(--brand);color:#fff;border:0;border-radius:8px;padding:8px 14px;font-size:13px;font-weight:600}
  .btn.ghost{background:#fff;border:1px solid var(--line);color:var(--ink)}
  .btn.sm{padding:5px 10px;font-size:12px}
  .btn.danger{background:#fff;border:1px solid #f0c4bb;color:var(--brand)}
  input,textarea,select{font-family:inherit;font-size:13px;width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--ink)}
  textarea{resize:vertical;min-height:60px}
  label{display:block;font-size:12px;color:var(--ink2);margin:10px 0 4px;font-weight:600}
  /* login */
  #login{max-width:360px;margin:12vh auto;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:28px;box-shadow:0 8px 30px rgba(0,0,0,.06)}
  #login h1{margin:0 0 4px;font-size:20px}
  #login p{margin:0 0 16px;color:var(--ink2);font-size:13px}
  .err{color:var(--brand);font-size:12px;min-height:16px;margin-top:8px}
  /* shell */
  #shell{display:none}
  .topbar{height:52px;background:var(--card);border-bottom:1px solid var(--line);display:flex;align-items:center;padding:0 16px;position:sticky;top:0;z-index:5}
  .topbar .logo{font-weight:800;color:var(--brand);font-size:16px}
  .topbar .spacer{flex:1}
  .side{width:190px;background:var(--card);border-right:1px solid var(--line);position:fixed;top:52px;bottom:0;padding:12px 8px;overflow:auto}
  .side button{display:block;width:100%;text-align:left;background:transparent;border:0;padding:10px 12px;border-radius:8px;color:var(--ink2);font-size:13px;font-weight:600;margin-bottom:2px}
  .side button.active,.side button:hover{background:#f0ede7;color:var(--ink)}
  .main{margin-left:190px;padding:20px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:16px}
  .card h2{margin:0 0 14px;font-size:16px}
  .grid{display:grid;gap:12px}
  .row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
  .row>*{flex:1;min-width:160px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
  th{color:var(--ink2);font-size:12px}
  .tag{display:inline-block;background:#f0ede7;border-radius:6px;padding:2px 8px;font-size:11px;color:var(--ink2);margin:2px 4px 2px 0}
  .muted{color:var(--ink2);font-size:12px}
  .stat{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;flex:1;min-width:150px}
  .stat .n{font-size:28px;font-weight:800;color:var(--brand)}
  .stat .l{color:var(--ink2);font-size:12px;margin-top:4px}
  /* modal */
  .mask{position:fixed;inset:0;background:rgba(20,18,15,.45);display:none;align-items:flex-start;justify-content:center;z-index:20;overflow:auto;padding:40px 12px}
  .mask.show{display:flex}
  .modal{background:var(--card);border-radius:14px;max-width:680px;width:100%;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.2)}
  .modal h3{margin:0 0 10px}
  .modal .acts{display:flex;gap:8px;justify-content:flex-end;margin-top:14px}
  .close{position:absolute}
  .toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1f1d1a;color:#fff;padding:10px 16px;border-radius:8px;font-size:13px;opacity:0;transition:.2s;z-index:30;pointer-events:none}
  .toast.show{opacity:1}
  .hint{font-size:11px;color:var(--ink2);margin-top:2px}
</style>
</head>
<body>
<div id="login">
  <h1>术语台 · 管理后台</h1>
  <p>登录后管理术语内容、站点设置、素材与账号</p>
  <label>用户名</label><input id="lu" placeholder="admin">
  <label>密码</label><input id="lp" type="password" placeholder="••••••" onkeydown="if(event.key==='Enter')doLogin()">
  <div class="err" id="lerr"></div>
  <div style="margin-top:14px"><button class="btn" style="width:100%" onclick="doLogin()">登录</button></div>
</div>

<div id="shell">
  <div class="topbar">
    <span class="logo">术语台后台</span>
    <span class="spacer"></span>
    <span class="muted" id="who"></span>
    <button class="btn ghost sm" style="margin-left:10px" onclick="doLogout()">退出</button>
  </div>
  <div class="side">
    <button data-tab="terms" class="active" onclick="switchTab('terms')">术语内容</button>
    <button data-tab="settings" onclick="switchTab('settings')">站点设置</button>
    <button data-tab="assets" onclick="switchTab('assets')">图片素材</button>
    <button data-tab="users" onclick="switchTab('users')">用户中心</button>
    <button data-tab="dashboard" onclick="switchTab('dashboard')">数据看板</button>
  </div>
  <div class="main">
    <div id="tab-terms" class="tab"></div>
    <div id="tab-settings" class="tab" style="display:none"></div>
    <div id="tab-assets" class="tab" style="display:none"></div>
    <div id="tab-users" class="tab" style="display:none"></div>
    <div id="tab-dashboard" class="tab" style="display:none"></div>
  </div>
</div>

<div class="mask" id="mask"><div class="modal" id="modal"></div></div>
<div class="toast" id="toast"></div>

<script>
const API="/admin/api";
let me=null;
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),1800);}
async function api(path,opts={}){const r=await fetch(API+path,Object.assign({headers:{'content-type':'application/json'}},opts));const j=await r.json().catch(()=>({}));if(r.status===401){location.reload();}return {status:r.status,data:j};}
async function doLogin(){const u=document.getElementById('lu').value, p=document.getElementById('lp').value;const {status,data}=await api('/login',{method:'POST',body:JSON.stringify({username:u,password:p})});if(status===200){me=data.user;enter();}else{document.getElementById('lerr').textContent=data.error||'登录失败';}}
async function doLogout(){await api('/logout',{method:'POST'});location.reload();}
async function enter(){document.getElementById('login').style.display='none';document.getElementById('shell').style.display='block';document.getElementById('who').textContent='你好，'+me;switchTab('terms');}
async function me_check(){const {data}=await api('/me');if(data.user){me=data.user;enter();}}

function switchTab(t){document.querySelectorAll('.side button').forEach(b=>b.classList.toggle('active',b.dataset.tab===t));document.querySelectorAll('.tab').forEach(el=>el.style.display='none');document.getElementById('tab-'+t).style.display='block';({'terms':loadTerms,'settings':loadSettings,'assets':loadAssets,'users':loadUsers,'dashboard':loadDashboard}[t])();}

/* ---------- 术语 ---------- */
let TERMS=[];
async function loadTerms(){const {data}=await api('/terms');TERMS=data.terms||[];const el=document.getElementById('tab-terms');el.innerHTML=\`<div class="card"><div class="row" style="align-items:flex-end"><div><label>搜索</label><input id="q" oninput="renderTerms()" placeholder="id / 中文名 / 英文"></div><div style="flex:0"><button class="btn" onclick="openTerm(0)">+ 新增术语</button></div></div></div><div class="card"><table><thead><tr><th>id</th><th>章</th><th>中文</th><th>英文</th><th>说法</th><th></th></tr></thead><tbody id="tlist"></tbody></table></div>\`;renderTerms();}
function renderTerms(){const q=(document.getElementById('q')||{}).value||'';const f=TERMS.filter(t=>(t.id+' '+(t.cn||'')+' '+(t.en||'')).toLowerCase().includes(q.toLowerCase()));document.getElementById('tlist').innerHTML=f.map(t=>\`<tr><td><code>\${t.id}</code></td><td>\${t.ch||''}</td><td>\${esc(t.cn||'')}</td><td>\${esc(t.en||'')}</td><td class="muted">\${esc((t.speak||'').slice(0,24))}</td><td style="text-align:right;white-space:nowrap"><button class="btn ghost sm" onclick="openTerm('\${t.id}')">编辑</button> <button class="btn danger sm" onclick="delTerm('\${t.id}')">删</button></td></tr>\`).join('')||'<tr><td colspan="6" class="muted">无</td></tr>';}
function fieldsHTML(t){t=t||{};return \`
<label>ID（唯一，英文短横线）</label><input id="f_id" value="\${t.id||''}" \${t.id?'disabled':''}>
<label>章节 ch</label><input id="f_ch" type="number" value="\${t.ch||0}">
<label>中文名 cn</label><input id="f_cn" value="\${esc(t.cn||'')}">
<label>英文名 en</label><input id="f_en" value="\${esc(t.en||'')}">
<label>大白话说法 speak</label><input id="f_speak" value="\${esc(t.speak||'')}">
<label>反模式描述 anti</label><textarea id="f_anti">\${esc(t.anti||'')}</textarea>
<label>正解说明 fix</label><textarea id="f_fix">\${esc(t.fix||'')}</textarea>
<label>代码·反例 bad</label><textarea id="f_bad">\${esc(t.bad||'')}</textarea>
<label>代码·正例 good</label><textarea id="f_good">\${esc(t.good||'')}</textarea>
<label>提示 tip（每行一条）</label><textarea id="f_tip">\${(t.tip||[]).join('\\n')}</textarea>
<label>平台提示 plat（web / app / mini）</label>
<div class="row">
<input id="f_pweb" placeholder="web" value="\${esc((t.plat&&t.plat.web)||'')}">
<input id="f_papp" placeholder="app" value="\${esc((t.plat&&t.plat.app)||'')}">
<input id="f_pmini" placeholder="mini" value="\${esc((t.plat&&t.plat.mini)||'')}">
</div>
<label>前后对照·错误态 HTML（vd_bad）</label><textarea id="f_vdbad">\${esc(t.vd_bad||'')}</textarea>
<label>前后对照·正确态 HTML（vd_good）</label><textarea id="f_vdgood">\${esc(t.vd_good||'')}</textarea>
\`;
}
async function openTerm(id){const t=id?TERMS.find(x=>x.id===id):null;document.getElementById('modal').innerHTML=\`<h3>\${id?'编辑术语':'新增术语'}</h3><div class="grid">\${fieldsHTML(t)}</div><div class="acts"><button class="btn ghost" onclick="closeModal()">取消</button><button class="btn" onclick="saveTerm('\${id||''}')">保存</button></div>\`;showModal();}
async function saveTerm(id){const plat={web:val('f_pweb'),app:val('f_papp'),mini:val('f_pmini')};const body={id:val('f_id')||id,ch:Number(val('f_ch')||0),speak:val('f_speak'),cn:val('f_cn'),en:val('f_en'),anti:val('f_anti'),fix:val('f_fix'),bad:val('f_bad'),good:val('f_good'),tip:val('f_tip').split('\\n').map(s=>s.trim()).filter(Boolean),plat, vd_bad:val('f_vdbad'),vd_good:val('f_vdgood')};if(!body.id){toast('ID 必填');return;}const {status,data}=id?await api('/term/'+encodeURIComponent(id),{method:'PUT',body:JSON.stringify(body)}):await api('/terms',{method:'POST',body:JSON.stringify(body)});if(status===200){toast('已保存，GitHub 将自动重建');closeModal();loadTerms();}else toast(data.error||'保存失败');}
async function delTerm(id){if(!confirm('确认删除 '+id+'？'))return;const {status}=await api('/term/'+encodeURIComponent(id),{method:'DELETE'});if(status===200){toast('已删除');loadTerms();}}

/* ---------- 设置 ---------- */
async function loadSettings(){const {data}=await api('/settings');const s=data.settings||{};const el=document.getElementById('tab-settings');el.innerHTML=\`<div class="card"><h2>站点设置</h2><div class="grid">
<label>站点标题 title</label><input id="s_title" value="\${esc(s.title||'')}">
<label>描述 description</label><textarea id="s_desc">\${esc(s.description||'')}</textarea>
<label>导航栏文案 nav</label><input id="s_nav" value="\${esc(s.nav||'')}">
<label>主色 brand（hex）</label><input id="s_brand" value="\${esc(s.brand||'#C8442E')}">
<label>页脚 footer</label><input id="s_footer" value="\${esc(s.footer||'')}">
<label>百度统计/腾讯分析 ID（可选）</label><input id="s_analytics" value="\${esc(s.analytics||'')}"><div class="hint">填入后会注入统计脚本（仅在配置了值时）</div>
</div><div class="acts" style="justify-content:flex-end;margin-top:14px"><button class="btn" onclick="saveSettings()">保存设置</button></div></div>\`;}
async function saveSettings(){const body={title:val('s_title'),description:val('s_desc'),nav:val('s_nav'),brand:val('s_brand'),footer:val('s_footer'),analytics:val('s_analytics')};const {status,data}=await api('/settings',{method:'PUT',body:JSON.stringify(body)});toast(status===200?'已保存':'保存失败');}

/* ---------- 素材 ---------- */
async function loadAssets(){const {data}=await api('/assets');const a=data.assets||[];const el=document.getElementById('tab-assets');el.innerHTML=\`<div class="card"><h2>图片 / 素材管理</h2><div class="row" style="align-items:flex-end"><div><label>选择文件（图片/SVG）</label><input type="file" id="af"></div><div style="flex:0"><button class="btn" onclick="uploadAsset()">上传</button></div></div><div class="hint" style="margin:8px 0">上传后写入仓库 assets/ 目录，术语对照里可用 /assets/文件名 引用。</div></div><div class="card"><div class="grid" id="alist" style="grid-template-columns:repeat(auto-fill,minmax(140px,1fr))">\${a.map(x=>\`<div style="border:1px solid var(--line);border-radius:10px;padding:8px"><div style="height:90px;background:#f3f1ed;border-radius:6px;display:flex;align-items:center;justify-content:center;overflow:hidden"><img src="/assets/\${x.name}" style="max-width:100%;max-height:100%"></div><div class="muted" style="margin-top:6px;font-size:11px;word-break:break-all">\${esc(x.name)}</div><button class="btn danger sm" style="margin-top:6px;width:100%" onclick="delAsset('\${x.name}')">删除</button></div>\`).join('')||'<div class="muted">暂无素材</div>'}</div></div>\`;}
async function uploadAsset(){const f=document.getElementById('af').files[0];if(!f)return toast('请选择文件');const b64=await fileToB64(f);const {status,data}=await api('/assets',{method:'POST',body:JSON.stringify({name:f.name,base64:b64,type:f.type})});toast(status===200?'上传成功':'上传失败');if(status===200)loadAssets();}
async function delAsset(n){if(!confirm('删除 '+n+'?'))return;const {status}=await api('/assets/'+encodeURIComponent(n),{method:'DELETE'});if(status===200)loadAssets();}

/* ---------- 用户 ---------- */
async function loadUsers(){const {data}=await api('/users');const u=data.users||[];const el=document.getElementById('tab-users');el.innerHTML=\`<div class="card"><h2>用户中心（后台账号）</h2><div class="row" style="align-items:flex-end"><div><label>用户名</label><input id="u_name"></div><div><label>密码</label><input id="u_pw" type="password"></div><div><label>角色</label><select id="u_role"><option value="admin">admin</option><option value="editor">editor</option></select></div><div style="flex:0"><button class="btn" onclick="addUser()">添加</button></div></div></div><div class="card"><table><thead><tr><th>用户名</th><th>角色</th><th></th></tr></thead><tbody>\${u.map(x=>\`<tr><td>\${esc(x.username)}</td><td><span class="tag">\${esc(x.role)}</span></td><td style="text-align:right"><button class="btn danger sm" onclick="delUser('\${x.username}')">删除</button></td></tr>\`).join('')}</tbody></table><div class="hint" style="margin-top:8px">至少保留一个 admin 账号。密码以 PBKDF2 哈希存储，不存明文。</div></div>\`;}
async function addUser(){const body={username:val('u_name'),password:val('u_pw'),role:val('u_role')};if(!body.username||!body.password)return toast('用户名密码必填');const {status,data}=await api('/users',{method:'POST',body:JSON.stringify(body)});toast(status===200?'已添加':(data.error||'失败'));if(status===200)loadUsers();}
async function delUser(n){if(!confirm('删除 '+n+'?'))return;const {status,data}=await api('/users/'+encodeURIComponent(n),{method:'DELETE'});toast(status===200?'已删除':(data.error||'失败'));if(status===200)loadUsers();}

/* ---------- 看板 ---------- */
async function loadDashboard(){const {data}=await api('/dashboard');const s=data.stats||{};const el=document.getElementById('tab-dashboard');el.innerHTML=\`<div class="card"><h2>数据看板</h2><div class="row">
<div class="stat"><div class="n">\${s.terms||0}</div><div class="l">术语总数</div></div>
<div class="stat"><div class="n">\${s.assets||0}</div><div class="l">素材数</div></div>
<div class="stat"><div class="n">\${s.users||0}</div><div class="l">后台账号</div></div>
</div><div class="card"><h2>部署状态</h2><div class="muted">\${s.deploy||'本地模式（未配置 GitHub）'}</div><div class="hint" style="margin-top:6px">配置 GH_TOKEN / GH_REPO 后，保存即写回 GitHub 并触发 Cloudflare Pages 自动重建。</div></div>
<div class="card"><h2>访问统计</h2><div class="muted">接入百度统计 / Cloudflare Analytics 后此处展示流量。可在「站点设置」填入统计 ID。</div></div>
</div>\`;}

/* ---------- 工具 ---------- */
function val(id){const e=document.getElementById(id);return e?e.value:'';}
function esc(s){return (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function showModal(){document.getElementById('mask').classList.add('show');}
function closeModal(){document.getElementById('mask').classList.remove('show');}
document.getElementById('mask').addEventListener('click',e=>{if(e.target.id==='mask')closeModal();});
function fileToB64(f){return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result.split(',')[1]);r.onerror=rej;r.readAsDataURL(f);});}
me_check();
</script>
</body>
</html>`;
