#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,urllib.request
from pathlib import Path

def api(url):
    r=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json","User-Agent":"binit-profile-cards"})
    with urllib.request.urlopen(r,timeout=20) as x:return json.load(x)
def e(x):return str(x).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
def stat_svg(title,sub,lines,dark):
    bg='#0D1117' if dark else '#FFF'; fg='#F0F6FC' if dark else '#24292F'; muted='#8B949E' if dark else '#57606A'; border='#30363D' if dark else '#D0D7DE'; s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360"><rect x="1" y="1" width="898" height="358" rx="24" fill="{bg}" stroke="{border}"/><rect x="1" y="1" width="8" height="358" rx="4" fill="#0285FF"/><text x="45" y="62" fill="{fg}" font-family="system-ui" font-size="28" font-weight="700">{e(title)}</text><text x="45" y="94" fill="{muted}" font-family="system-ui" font-size="15">{e(sub)}</text>']
    y=145
    for k,v in lines:s += [f'<text x="55" y="{y}" fill="{muted}" font-family="system-ui" font-size="15">{e(k)}</text>',f'<text x="845" y="{y}" text-anchor="end" fill="{fg}" font-family="system-ui" font-size="20" font-weight="700">{e(v)}</text>']; y+=48
    s.append('</svg>'); return '\n'.join(s)
def project_svg(name,desc,stars,forks,lang,dark):
    bg='#0D1117' if dark else '#FFF'; fg='#F0F6FC' if dark else '#24292F'; muted='#8B949E' if dark else '#57606A'; border='#30363D' if dark else '#D0D7DE'
    d=e(desc); a=[d[:95],d[95:190]]
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 300"><rect x="1" y="1" width="818" height="298" rx="22" fill="{bg}" stroke="{border}"/><circle cx="52" cy="54" r="14" fill="#0285FF"/><text x="82" y="63" fill="{fg}" font-family="system-ui" font-size="25" font-weight="700">{e(name)}</text><text x="40" y="115" fill="{muted}" font-family="system-ui" font-size="16">{a[0]}</text><text x="40" y="145" fill="{muted}" font-family="system-ui" font-size="16">{a[1]}</text><line x1="40" y1="185" x2="780" y2="185" stroke="{border}"/><text x="40" y="225" fill="{muted}" font-family="system-ui" font-size="15">Stars</text><text x="100" y="225" fill="{fg}" font-family="system-ui" font-size="18" font-weight="700">{stars}</text><text x="190" y="225" fill="{muted}" font-family="system-ui" font-size="15">Forks</text><text x="250" y="225" fill="{fg}" font-family="system-ui" font-size="18" font-weight="700">{forks}</text><text x="340" y="225" fill="{muted}" font-family="system-ui" font-size="15">Language</text><text x="430" y="225" fill="{fg}" font-family="system-ui" font-size="18" font-weight="700">{e(lang or "N/A")}</text></svg>'
def main():
    p=argparse.ArgumentParser(); p.add_argument('--user',required=True); p.add_argument('--out',default='assets'); a=p.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    user=api(f'https://api.github.com/users/{a.user}'); repos=api(f'https://api.github.com/users/{a.user}/repos?per_page=100&sort=updated'); by={r['name'].lower():r for r in repos}
    lines=[('Public repositories',user.get('public_repos',0)),('Followers',user.get('followers',0)),('Following',user.get('following',0)),('Public gists',user.get('public_gists',0))]
    for dark in (True,False):out.joinpath('stats-'+('dark' if dark else 'light')+'.svg').write_text(stat_svg(f'{a.user} · GitHub snapshot','Generated from the GitHub REST API',lines,dark),encoding='utf-8')
    projects=json.loads(out.joinpath('projects.json').read_text())['projects'][:4]
    for i,pr in enumerate(projects,1):
        r=by.get(pr['repo'].lower()); name=r['name'] if r else pr['repo']; desc=pr.get('description') or (r.get('description') if r else '') or 'Replace this repository in assets/projects.json'; stars=r.get('stargazers_count',0) if r else 0; forks=r.get('forks_count',0) if r else 0; lang=r.get('language') if r else 'N/A'
        for dark in (True,False):out.joinpath(f'card-project-{i}-'+('dark' if dark else 'light')+'.svg').write_text(project_svg(name,desc,stars,forks,lang,dark),encoding='utf-8')
if __name__=='__main__':main()
