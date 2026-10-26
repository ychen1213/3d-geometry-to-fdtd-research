# 从三维工艺结构到自研 FDTD

面向第一次接触三维文件表达的读者，用中文解释体素、表面网格、CAD、隐式场与其他表示方法，再用实际 Coventor AH53 转换记录讨论自研 FDTD 的技术选型。

**本报告以 10 nm 位置测量偏差为研究目标，另讨论 1 nm / 0.1 nm 两档。目标尚未经过三维工艺结构的完整光学验收。** 资源分析覆盖现有电脑与更大工作站；实施建议同时比较现有程序升级和面向三维的架构设计。

## 阅读

- [在线教程](https://ychen1213.github.io/3d-geometry-to-fdtd-research/)
- [教程源文件](index.html)
- 离线阅读：点击 GitHub 的 **Code → Download ZIP**，解压后双击 `index.html`。不需要安装 Python、Coventor 或 Lumerical，不需要 CDN 或远程字体。
- 页面提供目录、交互边界示例、内存数量级计算器和相位预算换算，可使用页面按钮打印为 PDF。

## 内容

1. **零基础三维表达。** 什么是点云、三角网格、材料体素、占比、稀疏体素、八叉树、距离场、CAD 实体、体网格；表示方法与文件容器有什么区别。
2. **转换和压缩。** 表面提取、体素化、减面、共享顶点、共面合并和无损编码分别改变什么信息。
3. **真实历史实验。** 二值 MAT、占比等值面、界面平面辅助重建、原生表面、独立 VDATA 转换、QEM 七档、40 种无损编码组合，以及两个 FDTD 短跑。
4. **Lumerical 与自研 FDTD。** 从输入几何到 Yee 网格，讨论界面映射、色散材料、PML、CPU/GPU、内存和时间、有限 mark 与周期读出、位置偏差验收。
5. **选型与实验路线。** 在明确适用条件下选择首版入口和中间数据协议，用同一测量链路比较未减面、减面和富体素输入。

## 证据边界

- 原 wafer 导出的表面，与独立 VDATA 转换，是两条不同路线，教程分别说明。
- 二值导入的巨大 FSP 涉及稠密 float64 接口，不能归纳为所有体素表示必然低效。
- QEM 的几何采样距离不等于严格 Hausdorff 上界，也不等于位置读数误差。
- CAD 几何内存与电磁求解场内存分别报告。
- 40/60 nm 网格只完成过约 100 fs 性能短跑；更细网格是 checker 预估，1 ps 时间是外推。
- 当前没有完成三种几何入口之间的完整三维光学定位误差对照。本报告不把建议或资源估算标为已达标实验。
- 本次工作是研究整理、证据审查和教程制作，没有重跑工艺或启动新的大规模电磁仿真。

## 文件结构

```text
index.html                  可直接打开的完整教程
assets/                     样式、交互逻辑、原创示意图与历史实验图
chapters/                   各部分 HTML 内容片段（由构建脚本合并）
evidence/
  history_metrics.json      历史转换、压缩、几何和资源数值
  history_provenance.json    原报告项目相对路径、字段定位、SHA256
  resource_metrics.json     9 档资源预检和 2 次实际短跑摘录
  solver_context.json       现有自研分支、指标和适用范围
  references_*.json         原始论文和官方文档索引
  build_manifest.json       构建计数、源章节哈希与范围声明
  quality_check.json        发布前页面与交互检查
tools/
  build_site.py             仅标准库：合并教程
  collect_resources.py      从已有资源报告提取公开数值
  make_figures.py           从公开数值重建图表（需 matplotlib）
  validate_site.py          检查本地链接、HTML结构与数据文件
```

历史来源路径相对于原工作目录 `D:\CoventorProjects`，方便原项目持有人追溯；阅读公开教程无需该目录。公开包含数值摘录和原报告哈希，不含大模型、完整求解工程、SDK、材料数据库或许可证。

## 重建与检查

直接阅读无需任何依赖。修改章节后可在仓库根目录运行：

```bash
python tools/build_site.py
python tools/validate_site.py
```

重建本报告的静态数量图（不会运行 FDTD）：

```bash
python -m pip install matplotlib
python tools/make_figures.py
```

Windows 下优先使用 Microsoft YaHei；其他系统绘图需要安装可显示中文的字体。已发布的 SVG/PNG 可直接使用。

重新提取本地历史资源报告时，明确传入原文件：

```bash
python tools/collect_resources.py --source "D:/CoventorProjects/AH53_FDTD_RunStudy/results.json"
```

## 日期与参考资料

整理日期 **2026-10-26**。各论点旁提供原始论文、官方文档或本项目证据链接。工程推断、未执行的方法与待验证的方案在正文标明。外部参考资料仍归各自权利人所有，本仓库不转载供应商手册。
