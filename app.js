const topics = ['All stories', 'Policy & oversight', 'Health equity', 'Privacy & data', 'Safety & standards'];
const art = {'Policy & oversight':['policy','§'], 'Health equity':['equity','◈'], 'Privacy & data':['privacy','⌘'], 'Safety & standards':['safety','✳']};
let articles = [], active = topics[0];
const el = id => document.getElementById(id);
const date = value => new Intl.DateTimeFormat('en-US',{month:'short',day:'numeric',year:'numeric'}).format(new Date(value));
function safeLink(value) {try {const u=new URL(value);return u.protocol==='https:' ? u.href : null;}catch{return null;}}
function node(tag, cls, text) {const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;}
function render() {
  const query=el('search').value.trim().toLowerCase();
  const selected=articles.filter(a => (active===topics[0] || a.topic===active) && `${a.title} ${a.source} ${a.description} ${a.topic}`.toLowerCase().includes(query));
  el('stories').replaceChildren(); el('count').textContent=`${selected.length} ${selected.length===1?'story':'stories'}`;el('empty').hidden=selected.length>0;
  for(const a of selected){
    const href=safeLink(a.url);if(!href)continue;
    const [style,symbol]=art[a.topic]||art[topics[1]];
    const card=node('article','story'), graphic=node('div',`story-art ${style}`);graphic.setAttribute('aria-hidden','true');graphic.append(node('span','art-symbol',symbol),node('span','art-label',a.topic.toUpperCase()));
    const body=node('div','story-content'), meta=node('div','story-meta');meta.append(node('span','',a.topic),node('span','',date(a.publishedAt)));
    const heading=node('h3'), link=node('a','',a.title);link.href=href;link.target='_blank';link.rel='noopener noreferrer';heading.append(link);
    const bottom=node('div','story-bottom'), read=node('a','','Read original ↗');read.href=href;read.target='_blank';read.rel='noopener noreferrer';read.setAttribute('aria-label',`Read original: ${a.title}`);bottom.append(node('span','source',a.source),read);
    body.append(meta,heading,node('p','story-description',a.description),bottom);card.append(graphic,body);el('stories').append(card);
  }
}
for(const topic of topics){const b=node('button','',topic);b.type='button';b.setAttribute('aria-pressed',String(topic===active));b.addEventListener('click',()=>{active=topic;for(const x of el('filters').children)x.setAttribute('aria-pressed',String(x===b));render();});el('filters').append(b);}
el('search').addEventListener('input',render);
async function load(){try{const response=await fetch('./data/articles.json',{cache:'no-cache'});if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=await response.json();articles=data.articles.filter(a=>a.title&&safeLink(a.url)&&Number.isFinite(Date.parse(a.publishedAt)));if(data.updatedAt)el('updated').textContent=`Last collected ${date(data.updatedAt)} · Updated daily`;if(data.demo){el('notice').hidden=false;el('notice').textContent='Design preview: the cards below are illustrative topic examples, not collected news articles. Live reporting will replace them after the first successful collection.';}else if(data.warning){el('notice').hidden=false;el('notice').textContent=data.warning;}render();}catch(e){el('notice').hidden=false;el('notice').textContent='The briefing could not be loaded. Please try again shortly.';el('empty').hidden=false;el('count').textContent='Unavailable';}}
load();
