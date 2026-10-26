# -*- coding: utf-8 -*-
"""Build the standalone HTML tutorial using only the Python standard library."""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=['00_start.html','01_representations.html','02_history.html','03_fdtd.html','04_workshop.html']
REPO='https://github.com/ychen1213/3d-geometry-to-fdtd-research'

def strip_tags(s):return html.unescape(re.sub('<[^>]+>','',s))

def main():
    parts=[]
    for name in FILES:
        p=ROOT/'chapters'/name
        if not p.exists():raise RuntimeError('Missing chapter: '+name)
        text=p.read_text(encoding='utf-8-sig')
        if name=='01_representations.html':text=text.replace('<h2>','<h2>第一部分 · ',1)
        if name=='03_fdtd.html':text=text.replace('<h2>','<h2>第三部分 · ',1)
        parts.append(text)
    body='\n'.join(parts)
    body=body.replace('class="table-wrap"','class="table-scroll"')
    # Every table remains usable on a narrow viewport, including with JS disabled.
    original=body
    def wrap(m):
        prefix=original[max(0,m.start()-100):m.start()]
        if re.search(r'<div class="table-scroll">\s*$',prefix):return m.group(0)
        return '<div class="table-scroll">'+m.group(0)+'</div>'
    body=re.sub(r'<table\b[^>]*>[\s\S]*?</table>',wrap,original)
    toc=[]
    def heading(m):
        level,attrs,inner=m.group(1),m.group(2),m.group(3)
        existing=re.search(r'\bid="([^"]+)"',attrs)
        ident=existing.group(1) if existing else 'heading-{:03d}'.format(len(toc)+1)
        if not existing:attrs+=' id="'+ident+'"'
        toc.append((level,ident,strip_tags(inner)))
        return '<h{}{}>{}</h{}>'.format(level,attrs,inner,level)
    body=re.sub(r'<h([23])([^>]*)>([\s\S]*?)</h\1>',heading,body)
    refs=[]
    for p in sorted((ROOT/'evidence').glob('references_*.json')):
        data=json.loads(p.read_text(encoding='utf-8-sig'))
        refs.extend(data if isinstance(data,list) else data.get('references',[]))
    seen=set(); unique=[]
    for r in refs:
        if r['url'] in seen:continue
        seen.add(r['url']);unique.append(r)
    refs_html=''.join('<li id="ref-{}"><a href="{}" target="_blank" rel="noopener noreferrer">{}</a><div class="claim">{}</div><small>核验日期：{}</small></li>'.format(html.escape(str(r.get('id',i))),html.escape(r['url'],quote=True),html.escape(r['title']),html.escape(r.get('claim','')),html.escape(r.get('accessed','2026-10-26'))) for i,r in enumerate(unique,1))
    body+='<section id="references"><h2>参考文献与证据索引</h2><p>以下以原始论文、官方文档及项目本地证据为主；正文在相关论点附近提供链接。资料描述算法或接口的一般能力，不能替代本项目的精度验证。网页核验日期为 2026-10-26。</p><ol class="references">'+refs_html+'</ol><p>历史数字：<a href="evidence/history_metrics.json">方法数据</a> · <a href="evidence/history_provenance.json">报告哈希及定位</a> · <a href="evidence/resource_metrics.json">资源数据</a> · <a href="evidence/solver_context.json">自研分支与指标定义</a> · <a href="evidence/quality_check.json">发布前页面检查</a>。</p></section>'
    toc.append(('2','references','参考文献与证据索引'))
    nav=''.join('<li class="toc-{}"><a href="#{}">{}</a></li>'.format(level,ident,html.escape(title)) for level,ident,title in toc)
    chinesecount=len(re.findall(r'[\u3400-\u9fff]',strip_tags(body)))
    doc='''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="从零理解三维表达，复盘 Coventor VDATA 到 Lumerical 的实测路线，并为 10 nm 位置测量课题选择自研 FDTD 几何与边界方案。"><title>从三维工艺结构到自研 FDTD · 3D 表达与计算选型调研</title><link rel="stylesheet" href="assets/style.css"><link rel="icon" href="data:,"></head>
<body id="top"><header class="hero"><p class="eyebrow">A research-backed guide · Geometry / Interfaces / FDTD</p><h1>从三维工艺结构<br>到自研 FDTD</h1><p>读懂体素、三角网格和其他三维表达；复盘已经走过的转换路线；围绕 10 nm 位置测量目标，比较精度、内存和实现成本。</p><p class="meta">2026-10-26 · 中文入门与技术选型 · 历史证据 + 原始文献 + 待验证方案 · 公开版</p><p class="meta"><a href="REPO">GitHub 源码与数据</a> · 离线打开 index.html 即可阅读 · 全文约 COUNT 万汉字</p></header>
<div class="layout"><aside class="sidebar"><strong>阅读目录</strong><div class="tools"><button id="mobile-nav" aria-expanded="false" type="button">展开目录</button><button id="print-button" type="button">打印 / 保存 PDF</button></div><progress id="reading-progress" max="1" value="0" aria-label="阅读进度"></progress><p class="status">重点：10 nm<br>扩展：1 nm / 0.1 nm<br>现有电脑 → 更强工作站</p><nav id="toc" aria-label="章节导航"><ol>NAV</ol></nav></aside><main>BODY<footer>本报告中的示意图和数值图由本项目生成，历史截图为本项目先前实验产物。公开文件包含教程、证据摘录与重建图表的脚本；供应商手册、SDK、许可证及完整大模型不在发布包内。引用的外部资料归各自权利人所有。<br>当前精度路线为研究建议；本次没有启动新的电磁求解或工艺仿真。</footer></main></div><a class="backtop" href="#top">回到顶部 ↑</a><script src="assets/app.js"></script></body></html>'''
    doc=doc.replace('REPO',REPO).replace('COUNT','{:.1f}'.format(chinesecount/10000)).replace('NAV',nav).replace('BODY',body)
    (ROOT/'index.html').write_text(doc,encoding='utf-8')
    manifest={'date':'2026-10-26','chinese_characters':chinesecount,'headings':len(toc),'references':len(unique),'chapters':[],'target_position_error_nm':10,'secondary_targets_nm':[1,.1],'new_electromagnetic_simulations':False,'publication_visibility':'public'}
    for name in FILES:
        raw=(ROOT/'chapters'/name).read_bytes();manifest['chapters'].append({'path':'chapters/'+name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    (ROOT/'evidence/build_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:manifest[k] for k in ('chinese_characters','headings','references')},ensure_ascii=False))

if __name__=='__main__':main()
