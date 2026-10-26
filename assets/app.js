"use strict";
const byId = id => document.getElementById(id);
function drawBoundary() {
  const h = Number(byId('demo-step').value), shift = Number(byId('demo-shift').value);
  byId('demo-shift-value').textContent = `${shift} nm`;
  const boundary = z => 158 + .24 * (z - 150) + 13 * Math.sin(z / 37) + shift;
  const W = 320, H = 280, ox = 25, oy = 22;
  let labelArea = 0, fracArea = 0;
  ['label', 'fraction', 'surface'].forEach(kind => {
    const ctx = byId(`canvas-${kind}`).getContext('2d');
    ctx.clearRect(0, 0, 360, 340);
    ctx.save(); ctx.translate(ox, oy);
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);
    if (kind !== 'surface') {
      for (let y = 0; y < H; y += h) for (let x = 0; x < W; x += h) {
        const w = Math.min(h, W - x), hh = Math.min(h, H - y);
        let f = 0;
        if (kind === 'label') f = x + w / 2 < boundary(H - y - hh / 2) ? 1 : 0;
        else {
          for (let j = 0; j < 24; j++) {
            const z = H - y - (j + .5) * hh / 24;
            f += Math.max(0, Math.min(w, boundary(z) - x)) / w / 24;
          }
        }
        ctx.fillStyle = `rgba(18,103,130,${f * .76})`; ctx.fillRect(x, y, w, hh);
        if (kind === 'label') labelArea += f * w * hh; else fracArea += f * w * hh;
      }
    } else {
      const pts = []; for (let z = 0; z <= H; z += 35) pts.push([boundary(z), H - z]);
      ctx.beginPath(); ctx.moveTo(0, H); pts.forEach(p => ctx.lineTo(...p)); ctx.lineTo(0, 0); ctx.closePath();
      ctx.fillStyle = '#b4dce1'; ctx.fill();
      ctx.beginPath(); pts.forEach((p,i) => i ? ctx.lineTo(...p) : ctx.moveTo(...p));
      ctx.strokeStyle = '#126782'; ctx.lineWidth = 2.5; ctx.stroke();
      ctx.fillStyle = '#126782'; pts.forEach(p => {ctx.beginPath();ctx.arc(...p,3,0,2*Math.PI);ctx.fill();});
    }
    ctx.strokeStyle = '#c4d4d8'; ctx.lineWidth = .6;
    for (let x = 0; x <= W; x += h) {ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
    for (let y = 0; y <= H; y += h) {ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
    ctx.beginPath(); for (let z = 0; z <= H; z++) z ? ctx.lineTo(boundary(z),H-z) : ctx.moveTo(boundary(z),H-z);
    ctx.strokeStyle='#bd6e37';ctx.setLineDash([5,4]);ctx.lineWidth=1.7;ctx.stroke();ctx.setLineDash([]);
    ctx.strokeStyle='#617c84';ctx.strokeRect(0,0,W,H);ctx.font='12px "Microsoft YaHei",sans-serif';
    ctx.fillStyle='#264c5a';ctx.fillText('硅',12,18);ctx.fillText('空气',W-42,18);ctx.fillText('x →（nm）',W-80,H+25);
    ctx.restore();
  });
  byId('boundary-result').textContent = `当前位移 ${shift} nm；网格 ${h} nm。该截面二值记录的硅面积 ${(labelArea/1e4).toFixed(3)} × 10⁴ nm²；占比记录约 ${(fracArea/1e4).toFixed(3)} × 10⁴ nm²。观察位移变化时两者的响应：保留占比与保留界面是不同的信息层次，二者都还需要电磁边界算法。`;
}
['demo-step','demo-shift'].forEach(id => byId(id)?.addEventListener('input',drawBoundary));
byId('demo-reset')?.addEventListener('click',()=>{byId('demo-step').value='40';byId('demo-shift').value='10';drawBoundary();});
if(byId('canvas-label')) drawBoundary();
function calcResources(){
  const h=Number(byId('calc-h').value), b=Number(byId('calc-bytes').value), ram=Number(byId('calc-ram').value), vram=Number(byId('calc-vram').value);
  byId('calc-h-value').textContent=`${h} nm`;
  const dims=[15.2,27.2,3.3], P=12, grid=dims.map(v=>Math.ceil(v*1000/h)+2*P);
  const N=grid.reduce((a,v)=>a*v,1), fields=N*24, all=N*b;
  const dt=.99*h*1e-9/(299792458*Math.sqrt(3)), steps=Math.ceil(1e-12/dt);
  const base=dims.map(v=>Math.ceil(v*1000/40)+2*P).reduce((a,v)=>a*v,1)*Math.ceil(1e-12/(.99*40e-9/(299792458*Math.sqrt(3))));
  const cap=(n,c)=>n/(2**30)<=c*.75?'在预留 25% 容量后可容纳这一简化估算':'超过预留 25% 后的容量';
  byId('calc-result').innerHTML=`<strong>教学网格：${grid.join(' × ')} ≈ ${(N/1e6).toFixed(2)} 百万单元</strong><br>6 个 float32 场分量下限：${(fields/1e9).toFixed(2)} GB（${(fields/2**30).toFixed(2)} GiB）。<br>按 ${b} B/单元假定的求解数据：${(all/1e9).toFixed(2)} GB（${(all/2**30).toFixed(2)} GiB）。<br>CFL 教学时间步约 ${(dt*1e15).toFixed(4)} fs；推进 1 ps 约 ${steps.toLocaleString()} 步；单元更新总量为 40 nm 示例的 <strong>${(N*steps/base).toFixed(2)} 倍</strong>。<br>${ram} GiB 系统内存：${cap(all,ram)}。<br>${vram} GiB 单卡显存：${cap(all,vram)}。`;
}
['calc-h','calc-bytes','calc-ram','calc-vram'].forEach(id=>byId(id)?.addEventListener('input',calcResources));
if(byId('calc-result'))calcResources();
function phaseBudget(){
  const L=Number(byId('phase-period').value), m=Number(byId('phase-order').value), target=Number(byId('phase-target').value);
  if(!(L>0&&m>=1&&target>0)){byId('phase-result').textContent='请输入正周期、有效衍射级次和正误差目标。';return;}
  const phi=4*Math.PI*m*target/(L*1000);
  byId('phase-result').textContent=`在已说明的周期自参考相位模型中，${target} nm 位置偏差对应相位偏差幅值 ${phi.toFixed(6)} rad（${(phi*180/Math.PI).toFixed(4)}°）。这只是相位误差与位置误差的代数换算，不是几何误差、反射率误差或有限 mark 绝对位置的换算公式。`;
}
['phase-period','phase-order','phase-target'].forEach(id=>byId(id)?.addEventListener('input',phaseBudget));
if(byId('phase-result'))phaseBudget();
byId('print-button')?.addEventListener('click',()=>window.print());
byId('mobile-nav')?.addEventListener('click',()=>{const side=document.querySelector('.sidebar');side.classList.toggle('open');byId('mobile-nav').setAttribute('aria-expanded',String(side.classList.contains('open')));});
const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){document.querySelectorAll('#toc a').forEach(a=>a.classList.toggle('active',a.getAttribute('href')===`#${e.target.id}`));}},{rootMargin:'-10% 0px -70% 0px'});
document.querySelectorAll('main h2[id],main h3[id]').forEach(s=>observer.observe(s));
window.addEventListener('scroll',()=>{const max=document.documentElement.scrollHeight-innerHeight;byId('reading-progress').value=max?scrollY/max:0;},{passive:true});
