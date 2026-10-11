const articles=window.ARTICLES||[];
const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let selectedTopic='',query='';
const score=a=>a.score===null||a.score===undefined?'未評分':`${a.score}${a.scoreMax?` / ${a.scoreMax}`:''}`;
function hashLink(a){return '#article='+encodeURIComponent(a.id)}
function renderLibrary(){
 const topics=[...new Set(articles.map(a=>a.topic))];
 $('topics').replaceChildren();
 for(const topic of ['',...topics]){const button=document.createElement('button');button.type='button';button.className='topic'+(topic===selectedTopic?' active':'');button.setAttribute('aria-pressed',String(topic===selectedTopic));const title=document.createElement('span');title.textContent=topic||'全部題目';const count=document.createElement('small');count.textContent=articles.filter(a=>!topic||a.topic===topic).length;button.append(title,count);button.onclick=()=>{selectedTopic=topic;renderLibrary()};$('topics').append(button)}
 const rows=articles.filter(a=>(!selectedTopic||a.topic===selectedTopic)&&[a.topic,a.label,a.summary,...a.paragraphs,...a.learn,...a.improve].join(' ').toLocaleLowerCase().includes(query.toLocaleLowerCase()));
 $('catalog-title').textContent=selectedTopic||'全部佳作';$('count').textContent=`${rows.length} 篇佳作${query?'符合搜尋':''}`;
 $('results').innerHTML=rows.length?rows.map(a=>`<a class="entry" href="${hashLink(a)}"><span class="entry-number">${String(articles.indexOf(a)+1).padStart(2,'0')}</span><div><h3>${esc(a.label)}</h3><p>${esc(a.summary||'內容大意待補充。')}</p><div class="meta"><span>${esc(a.topic)}</span><span>${a.words} 字</span><span>閱讀全文及參考賞析 →</span></div></div><span class="score">${esc(score(a))}</span></a>`).join(''):'<div class="empty"><p>沒有符合條件的文章。試試其他關鍵字或作文題目。</p><button class="secondary" id="reset">清除篩選</button></div>';
 if($('reset'))$('reset').onclick=()=>{selectedTopic='';query='';$('query').value='';renderLibrary()};
}
function list(items){return items.length?`<ul>${items.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>`:'<p>待補充。</p>'}
function route(){
 const params=new URLSearchParams(location.hash.slice(1)),id=params.get('article');
 if(!id){$('library').hidden=false;$('reader').hidden=true;document.title='文學佳作・閱讀與寫作';renderLibrary();return}
 const a=articles.find(x=>x.id===id);$('library').hidden=true;$('reader').hidden=false;
 if(!a){$('reader').innerHTML='<div class="empty"><h1>找不到這篇文章</h1><p>文章連結可能已更新。</p><a href="#">返回文章庫</a></div>';return}
 document.title=a.label+'｜文學佳作';
 const siblings=articles.filter(x=>x.topic===a.topic),i=siblings.indexOf(a);
 $('reader').innerHTML=`<div class="reader-top"><a class="back" href="#">← 返回佳作文章庫</a><div class="reading-tools"><span>閱讀字體</span><button id="smaller" aria-label="縮小閱讀字體">A−</button><button id="larger" aria-label="放大閱讀字體">A＋</button></div></div><div class="reader-heading"><p class="eyebrow">${esc(a.topic)} · 佳作 ${i+1}</p><h1 tabindex="-1" id="article-title">${esc(a.label)}</h1><p class="label">作文題目：${esc(a.topic)}</p><div class="teacher-score">教師分數：<strong>${esc(score(a))}</strong> · ${a.words} 字</div></div><div class="reader-grid"><div><p class="article-note">以下全文依 Word 匯入，統一轉為繁體；原有用詞、標點及不清標記保留。「${esc(a.label)}」為閱讀辨識名稱。</p><article class="article"><h2>佳作全文</h2>${a.paragraphs.map(p=>`<p>${esc(p)}</p>`).join('')}</article></div><aside class="notes" aria-label="文章參考資料"><h2>內容大意</h2><p>${esc(a.summary||'待補充。')}</p><h2>值得學習之處</h2>${list(a.learn)}<h2>有待改善之處</h2>${list(a.improve)}<p class="source-note">評語來源：${esc(a.reviewSource)}。<br>教師分數獨立記錄，未提供時顯示「未評分」。</p></aside></div><nav class="article-nav" aria-label="同題佳作">${i>0?`<a href="${hashLink(siblings[i-1])}">← 上一篇：${esc(siblings[i-1].label)}</a>`:'<span></span>'}${i<siblings.length-1?`<a href="${hashLink(siblings[i+1])}">下一篇：${esc(siblings[i+1].label)} →</a>`:''}</nav>`;
 let size=19;try{size=Math.min(26,Math.max(16,Number(localStorage.getItem('reading-size'))||19))}catch{}
 const resize=delta=>{size=Math.min(26,Math.max(16,size+delta));$('reader').style.setProperty('--reading-size',size+'px');try{localStorage.setItem('reading-size',size)}catch{}};
 resize(0);$('smaller').onclick=()=>resize(-1);$('larger').onclick=()=>resize(1);window.scrollTo(0,0);$('article-title').focus({preventScroll:true});
}
$('query').addEventListener('input',e=>{query=e.target.value;renderLibrary()});window.addEventListener('hashchange',route);route();
