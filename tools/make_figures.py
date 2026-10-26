"""Rebuild original research figures from the published numerical evidence.
Requires matplotlib; no solver, vendor SDK or raw 3D model is needed.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'
font=Path('C:/Windows/Fonts/msyh.ttc')
if font.exists():
    font_manager.fontManager.addfont(str(font)) if hasattr(font_manager.fontManager,'addfont') else None
    plt.rcParams['font.family']=font_manager.FontProperties(fname=str(font)).get_name()
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','axes.unicode_minus':False})

def resources():
    d=json.loads((ROOT/'evidence/resource_metrics.json').read_text(encoding='utf-8'))
    a=sorted([c for c in d['cases'] if not c['graded']],key=lambda c:c['requested_step_nm'],reverse=True)
    x=list(range(len(a))); val=[c['recommended_bytes']/1e9 for c in a]
    fig,ax=plt.subplots(figsize=(10.8,5.6));fig.patch.set_facecolor('#f7faf9');ax.set_facecolor('#f7faf9')
    ax.bar(x,val,color='#6ba5b7',width=.58,label='checker 估计，未代表完整光学求解')
    for p in d['pilots']:
        i=next(i for i,c in enumerate(a) if c['case']==p['case'])
        ax.scatter([i],[p['peak_engine_reported_bytes']/1e9],marker='D',s=70,color='#ba7036',zorder=4,label='100 fs 短跑实际峰值' if i==0 else None)
    peaks={p['case']:p['peak_engine_reported_bytes']/1e9 for p in d['pilots']}
    for i,v in enumerate(val):
        label_y=max(v,peaks.get(a[i]['case'],0))*1.16
        ax.text(i,label_y,'{:.2f}'.format(v),ha='center',va='bottom',fontsize=10)
    ax.set_yscale('log');ax.set_ylim(.5,2500);ax.set_xticks(x);ax.set_xticklabels([str(c['requested_step_nm']) for c in a])
    ax.set_xlabel('均匀网格间距 / nm');ax.set_ylabel('内存 / GB（十进制，对数轴）');ax.grid(axis='y',alpha=.22,which='both')
    ax.set_title('同一 QEM45 工程：几何很小，求解内存仍随网格迅速增加',loc='left',pad=18,fontweight='bold')
    ax.legend(loc='upper left',frameon=False,fontsize=10)
    fig.text(.1,.015,'历史设置：532 nm，CPU 8 线程；40/60 nm 仅短跑。其余为 checker 估计；无位置精度验收。',fontsize=9,color='#506771')
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(str(OUT/'resource_memory.svg'));fig.savefig(str(OUT/'resource_memory.png'),dpi=180);plt.close(fig)

def storage():
    d=json.loads((ROOT/'evidence/history_metrics.json').read_text(encoding='utf-8'))
    vals=[('源 VDATA（压缩工艺数据）',d['standalone_vdata']['source_metadata']['file_bytes'],'#536e7f')]
    for f in d['binary_full']['file_sizes']:
        if '/full/' not in f['project_relative_path']:
            continue
        if f['project_relative_path'].endswith('.mat'):vals.append(('二值 MAT（float64）',f['bytes'],'#c58d57'))
        elif f['project_relative_path'].endswith('.fsp'):vals.append(('二值导入 FSP',f['bytes'],'#c58d57'))
    vals.append(('未减面二进制 STL',d['lossless']['source_stl_bytes'],'#327a94'))
    for c in d['cad_storage']['cases']:
        if c['label'] in ('stl','qem_045p0','qem_065p0'):
            vals.append(({'stl':'未减面 FSP','qem_045p0':'QEM45 FSP','qem_065p0':'QEM65 FSP'}[c['label']],c['fsp_bytes'],'#327a94' if c['label']=='stl' else '#368e84'))
    vals.append(('索引几何 + LZMA（实验格式）',d['entropy']['best']['archive_bytes'],'#6d839e'))
    fig,ax=plt.subplots(figsize=(11,6));fig.patch.set_facecolor('#f7faf9');ax.set_facecolor('#f7faf9')
    y=list(range(len(vals)));ax.barh(y,[v[1]/1e6 for v in vals],color=[v[2] for v in vals],height=.62)
    ax.set_yticks(y);ax.set_yticklabels([v[0] for v in vals]);ax.invert_yaxis();ax.set_xscale('log');ax.set_xlim(.6,1200)
    for i,v in enumerate(vals):ax.text(v[1]/1e6*1.1,i,'{:.3f} MB'.format(v[1]/1e6),va='center',fontsize=10)
    ax.set_xlabel('文件大小 / MB（十进制，对数轴）');ax.grid(axis='x',alpha=.22,which='both')
    ax.set_title('同一全范围样本的不同存储产物',loc='left',fontweight='bold',pad=16)
    fig.text(.06,.015,'文件语义不同；表面重建、QEM 与无损压缩必须分别评价。小文件不等于小电磁求解内存。',fontsize=9,color='#506771')
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(str(OUT/'storage_comparison.svg'));fig.savefig(str(OUT/'storage_comparison.png'),dpi=180);plt.close(fig)

def pipeline():
    boxes=[('01 工艺数据',['尺寸 / 材料 / 占比','原始 VDATA 与 wafer']),('02 几何表达',['体素 / 表面 / 隐式场','单位与坐标必须明确']),('03 材料映射',['查询界面与局部占比','生成 Yee 更新系数']),('04 电磁求解',['E / H / ADE / PML','推进时间并记录信号']),('05 位置读出',['参考与估计器','最终验证 10 nm 目标'])]
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="245" viewBox="0 0 1200 245"><title>从工艺文件到位置测量的计算流程</title><rect width="1200" height="245" fill="#f7faf9"/><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#3b788a"/></marker></defs>']
    for i,(title,lines) in enumerate(boxes):
        x=16+i*238
        parts.append('<rect x="{}" y="25" width="216" height="140" rx="9" fill="#e6f0f2" stroke="#aac8d1"/>'.format(x))
        parts.append('<text x="{}" y="62" font-size="19" font-weight="bold" fill="#174e5e">{}</text>'.format(x+17,title))
        for j,line in enumerate(lines):parts.append('<text x="{}" y="{}" font-size="15" fill="#355c69">{}</text>'.format(x+17,99+j*29,line))
        if i<4:parts.append('<path d="M{},95 h20" stroke="#3b788a" stroke-width="2" marker-end="url(#arrow)"/>'.format(x+216))
    parts.append('<text x="20" y="211" font-size="16" fill="#546d76">逐级验证：信息是否足够 → 边界是否改变 → 材料映射是否正确 → 电磁结果是否收敛 → 位置读数是否可信</text></svg>')
    (OUT/'pipeline.svg').write_text(''.join(parts),encoding='utf-8')

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    pipeline();resources();storage();print('Rebuilt 5 original figure files')
