"""Read-only checks for the generated report; no electromagnetic tests."""
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Checker(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self,convert_charrefs=True)
        self.ids=[];self.links=[];self.images=[];self.stack=[];self.errors=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        for k in ('href','src'):
            if a.get(k):self.links.append(a[k])
        if tag=='img':
            self.images.append(a.get('src'))
            if not a.get('alt'):self.errors.append('Image without descriptive alt: '+str(a.get('src')))
        if tag not in VOID:self.stack.append(tag)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if tag in VOID:return
        if not self.stack or self.stack[-1]!=tag:
            self.errors.append('Unbalanced closing '+tag+'; current='+repr(self.stack[-3:]))
            if tag in self.stack:
                while self.stack and self.stack[-1]!=tag:self.stack.pop()
                self.stack.pop()
        else:self.stack.pop()

def main():
    c=Checker();c.feed((ROOT/'index.html').read_text(encoding='utf-8'))
    errors=c.errors[:]
    if c.stack:errors.append('Unclosed tags: '+repr(c.stack))
    errors+=['Duplicate id: '+k for k,n in Counter(c.ids).items() if n>1]
    local=0;external=set()
    for link in c.links:
        u=urlsplit(link)
        if u.scheme in ('http','https'):external.add(link);continue
        if u.scheme=='data':continue
        if u.scheme:errors.append('Nonportable URL: '+link);continue
        if not u.path:
            if u.fragment and unquote(u.fragment) not in c.ids:errors.append('Missing anchor '+link)
            continue
        p=(ROOT/unquote(u.path)).resolve();local+=1
        if ROOT not in p.parents:errors.append('Escapes report package: '+link)
        elif not p.exists():errors.append('Missing local target: '+link)
    json_files=list((ROOT/'evidence').glob('*.json'))
    for p in json_files:
        try:json.loads(p.read_text(encoding='utf-8-sig'))
        except Exception as e:errors.append('Invalid JSON '+p.name+': '+str(e))
    report={'html_ids':len(c.ids),'image_count':len(c.images),'local_link_checks':local,'distinct_external_urls':len(external),'json_files':len(json_files),'errors':errors}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(1 if errors else 0)

if __name__=='__main__':main()
