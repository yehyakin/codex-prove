# 新版制作与检查记录

日期：2026-10-01，Asia/Shanghai。事实基线：`f4dba1c20b0dc299fbcf565bc883c5afdc0324a9`。
范围：三种主题、中英文各一版；不是六种不同主题，也不是项目正式发布。

## 实际检查

- 六版完整渲染退出码 0；1600×900、30 fps、180 帧、6 秒、无声 H.264/yuv420p、BT.709。
- 每版的封面 PNG 与第 156 帧完全一致，并保持到第 179 帧；首帧与封面不同。
- 六个 GIF 均为 90 帧、6000 ms。视频解码封面 RMS 依次为
  2.689 / 2.743 / 2.783 / 2.823 / 3.027 / 3.028，全部低于原定 4.0 门槛。
- 实际原图与渲染封面合并对照；六组局部文字对照、六组八帧联系表共 48 张抽帧完成视觉检查。
- 标题、页眉、页脚在所有抽帧中像素一致；证据主题的三个结论说明始终稳定显示。
- 六组 Live Photo：原生 JPG/MOV 配对标识、5.2 秒 timed metadata、PHLivePhoto 本机加载和资源哈希通过。
- 12 个 PNG/GIF 文件导出至 `docs/assets/readme/livecanvas/polish/`，SHA-256 与最终渲染记录逐一一致。
- 预览页响应与磁盘文件完全一致，52 个独立素材/下载/来源地址均为 HTTP 200 且非空；每种语言各五张卡片。
- 仓库验证器通过，README/SVG 子集 23 项通过（0.121 秒），`git diff --check` 通过。
  本机没有 `pwsh`，沿用仓库的确定性结构检查；未宣称 PowerShell 运行验证。
- PNG 原图和文字未用手工 SVG/CSS 重画。动效使用实际生成原图的曝光控制，文字不属于独立可编辑图层。

## 保留的首轮问题

1. 开场的矩形遮罩边界过于明显。按 Product Design 的对照检查要求列为 P2，
   改为柔和椭圆羽化并降低遮罩强度后，重新渲染全部六版。旧版留在
   `out/polish-attempt-1/` 和 `qa-output/polish-attempt-1/`，没有删除。
2. 仓库文档校验曾在 QA 文档尚未建立时发现链接目标缺失。
   通过建立实际检查报告解决，不改验证规则或降低门槛。

## 证据文件

- `out/source-evidence-polish.json`：候选源码、十条事实与两份来源。
- `assets-polish.json`：六个原图的来源、尺寸、提示词路径、SHA-256 和文字核实记录。
- `out/<版本>/render.json`：最终源代码、事实与素材哈希，媒体格式和产物哈希。
- `out/<版本>/image-qa.json`：精确封面帧、视频解码差异、GIF 帧数/时长。
- `qa-output/polish/comparison-receipt.json`：真实原图/渲染对照和稳定区域检查。
- `qa-output/gallery-resources.json`：更新后页面和 52 个资源的 HTTP 检查，不包含浏览器交互结论。
- `out/<版本>/live/manifest.json`：原生配对与本机加载结果。
- `out/<版本>/package-receipt.json`、`delivery.json`、`qa.json`：资源与交付范围。
- [design-qa.md](design-qa.md)：五项画面保真检查、P2 修复与复验。

## 验证边界

预览页已增加六版素材，并保留四个原版。资源链接可独立检查；
本轮没有运行预览页浏览器自动化，原版 `qa-output/browser-qa.json` 不能作为更新后页面的验收结果。
更新后的 `tools/verify-preview.mjs` 按十个版本读取各自媒体尺寸和时长；脚本语法检查不等于浏览器实测。

本机 PHLivePhoto 加载不等于 iPhone、照片导入、锁屏或社交平台验证。没有打开照片 App 或写入图库。
没有替换根目录 README/SVG，没有提交、推送、合并或发布；所有内容仅为本地候选。
