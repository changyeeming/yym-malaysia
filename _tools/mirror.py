#!/usr/bin/env python3
"""把網站每一頁的文字內容轉成 Obsidian .md（內容鏡像🦞），保證與線上一致。
用法：python3 _tools/mirror.py  （在 site 根目錄執行）"""
import os,re,html,sys,shutil,datetime
SITE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBS="/Users/yeemingchang/Library/Mobile Documents/iCloud~md~obsidian/Documents/2023/3. Project作/2026-08-26YYM吉隆坡/1. 內容鏡像🦞"
VER=os.environ.get('VER','第7版')
DATE=datetime.date.today().strftime('%m%d')
URL='https://changyeeming.github.io/yym-malaysia/'

def strip(s):
    s=re.sub(r'<script.*?</script>','',s,flags=re.S)
    s=re.sub(r'<style.*?</style>','',s,flags=re.S)
    return s

def to_md(path):
    raw=open(path,encoding='utf-8').read()
    title=re.search(r'<title>(.*?)</title>',raw,re.S).group(1).strip()
    body=strip(raw)
    # 抽 map 頁的點位（在 script 裡）給地圖頁用
    pts=[]
    for m in re.finditer(r"(?:pt|add)\('?(\w+)'?,?\s*([\d.]+),\s*([\d.]+),\s*'([^']*)',\s*'([^']*)'",raw):
        pts.append((m.group(4),m.group(5)))
    for m in re.finditer(r"\[([\d.]+),([\d.]+),'([^']*)','([^']*)'",raw):
        pts.append((m.group(3),m.group(4)))
    out=[]
    # 逐塊轉：h1/h2/h3/p/li/table/step/anchor
    body=re.sub(r'<br\s*/?>','\n',body)
    blocks=re.findall(r'<(h1|h2|h3|p|li|div class="(?:anchor[^"]*|eyebrow|sub|one|note|maplegend|d|t|what|how|alt|s|status)"|tr|footer)[^>]*>(.*?)</(?:h1|h2|h3|p|li|div|tr|footer)>',body,re.S)
    def txt(x):
        x=re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>',lambda m:f'[{re.sub("<[^>]+>","",m.group(2)).strip()}]({m.group(1)})',x,flags=re.S)
        x=re.sub(r'<s>(.*?)</s>',r'~~\1~~',x,flags=re.S)
        x=re.sub(r'<b>(.*?)</b>',r'**\1**',x,flags=re.S)
        x=re.sub(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>',r'\1 | ',x,flags=re.S)
        x=re.sub(r'<[^>]+>','',x)
        x=html.unescape(x)
        return re.sub(r'[ \t]+',' ',x).strip()
    for tag,inner in blocks:
        t=txt(inner)
        if not t: continue
        if tag=='h1': out.append(f'# {t}')
        elif tag=='h2': out.append(f'\n## {t}')
        elif tag=='h3': out.append(f'\n### {t}')
        elif tag=='li': out.append(f'- {t}')
        elif tag=='tr': out.append('| '+t.rstrip('| ').strip()+' |')
        elif tag=='footer': out.append(f'\n---\n_{t}_')
        elif tag.startswith('div class="t"') : out.append(f'\n**{t}**')
        elif tag.startswith('div class="what"'): out.append(f'{t}')
        elif tag.startswith('div class="how"'): out.append(f'  {t}')
        elif tag.startswith('div class="alt"'): out.append('  > '+re.sub(r'^備案[：:]\s*','',t))
        elif tag.startswith('div class="eyebrow"'): out.append(f'_{t}_')
        else: out.append(t)
    md='\n'.join(out)
    # 清掉巢狀重複（外層 div 已含內層文字時會重複），簡單去重連續相同行
    lines=[];prev=None
    for l in md.split('\n'):
        if l.strip() and l==prev: continue
        lines.append(l);prev=l
    md='\n'.join(lines)
    if pts and 'map/' in path:
        md+='\n\n## 地圖點位\n'+'\n'.join(f'- **{n}** — {d}' for n,d in pts)
    return title,md

pages=[('index.html','index'),('plan.html','plan'),('day/day1.html','day1'),('day/day2.html','day2'),('day/day3.html','day3'),('day/day4.html','day4'),('day/day5.html','day5'),('day/day6.html','day6'),('map/all.html','map-all'),('map/food.html','map-food'),('map/taste.html','map-taste')]
os.makedirs(OBS,exist_ok=True)
snap=os.path.join(OBS,'_版本',f'{VER}-{DATE}'); os.makedirs(snap,exist_ok=True)
for rel,name in pages:
    title,md=to_md(os.path.join(SITE,rel))
    header=f'---\nsource: {URL}{rel}\nversion: {VER}\nsynced: {datetime.date.today().isoformat()}\n---\n> 🦞 內容鏡像 · 與線上一致 · 改這裡後跟 Claude 說「照 {name}.md 更新網站」\n\n'
    for d in (OBS,snap):
        open(os.path.join(d,f'{name}.md'),'w',encoding='utf-8').write(header+md+'\n')
print(f'mirrored {len(pages)} pages -> {OBS} (+snapshot {VER}-{DATE})')
