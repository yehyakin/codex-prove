# Codex PROVE · LiveCanvas 配图

> 制作档案：下文“候选／未发布”及 manifest 状态记录 2026-10-01 接入检查时的事实，不表示当前发布状态。当前版本以 [v1.2.0 Release](https://github.com/yehyakin/codex-prove/releases/tag/v1.2.0) 为准；素材、日期与哈希保持不变。

六种主题，中英文各一版。源自用户指定的 [LiveCanvas](https://github.com/pengchujin/livecanvas)。
原版两种主题使用代码图形；新增三种主题采用用户选定的 Product Design 第一稿，
用生成图片与 Remotion 逐帧动效说明任务路由、写入负责人和交付证据。
另补一组同风格的成本机制图：少传上下文、少开空代理；明确标记为设计目标，不宣称实测节省。
成本主题现增加预算版，预览默认显示相对全程 Astra 的 **82.8% 示例节省**：375 → 64.5 credits。
假设输入、输出均为 Sol 6.1 80% / Luna 20%，另加 3.75 credits 协调开销；这是预算，不是实测或固定配额。
原成本机制图及其全部导出保留。中英预算版仍属同一成本主题，不增加主题计数。

新版沿用深蓝底、浅色标题和橙／薄荷／紫色路径。海报文字保存在图片里，
修改措辞可使用完整提示词；动效顺序与时间在 `src/polish.tsx` 中编辑。

本地中英文 README 已接入成本预算、分工、交付验真和写入负责人四组图：PNG 内嵌，GIF 按需打开。原版 SVG 与各轮导出保留，**没有提交、推送、合并或发布**。

## 文件

- `preview.html`：中英切换、动画/静态切换；尊重减少动效设置。
- `src/index.tsx`：四个可编辑的 Remotion composition（两种主题的中英翻译版本）。
- `src/polish.tsx`：新增三种主题、六个 composition；原图及提示词在 `public/media/polish/`。
- `src/cost.tsx`：补充成本主题的中英文动效；事实、来源、素材分别在 `data-cost.json`、`sources-cost.md`、`assets-cost.json`。
- `src/cost-budget.tsx`：预算版中英文动效；对应 `data-cost-budget.json`、`sources-cost-budget.md`、`assets-cost-budget.json`，官方费率摘录在 `evidence/cost-budget-rates.json`。
- `series.json`：保留原版与新版的入口、版本清单和封面帧，默认仍制作原版。
- `data.json` / `sources.md`：事实、源码摘录、日期和证据范围。
- `data-polish.json` / `sources-polish.md`：新增三种主题的十条来源核实与生成素材说明。
- `assets.json`：原创示意素材、系统字体和使用说明。
- `out/{roles,solo}-{zh,en}/`：每版的 PNG/JPG、GIF、MP4、配对资源、Live Photo 包与验收记录。
- `out/{routing,ownership,evidence}-{zh,en}/`：选定风格的六个新版交付目录。
- `out/cost-{zh,en}/`：成本主题的两个交付目录。
- `out/cost-budget-{zh,en}/`：成本预算版两个交付目录；轻量 PNG/GIF 在 `../../assets/readme/livecanvas/cost-budget/`。
- `qa-output/`：桌面/窄屏预览、动画抽帧、浏览器检查记录。
- `../../assets/readme/livecanvas/`：供项目选用的轻量 PNG/GIF 配图副本。
- `../../assets/readme/livecanvas/polish/`：新版副本，不覆盖原版文件。
- `../../assets/readme/livecanvas/cost/`：成本主题 PNG/GIF 副本。

`node_modules`、编译器缓存、试制与完整交付输出不进入 Git。需要分享 Live Photo 或 MP4 时使用本地 `out/` 成品，或按下面的命令重建。
第一轮的格式/色差检查失败保留在制作记录中；试制输出在 `out/attempt-*`，不是推荐使用的成品。

## 重建

需要 Node.js/npm。锁定 LiveCanvas 模板原有的 Remotion 4.0.530，未升级依赖或全局安装技能。
所有渲染都使用本地素材，不调用图片服务。原版中文使用渲染机的 PingFang SC；
新版文字已经位于 PNG 原图中，渲染时不依赖系统字体。

```sh
cd docs/visuals/livecanvas
npm ci --no-audit --no-fund
node validate.mjs
npm run typecheck
npm run render
# 新版（不会覆盖原版）：
node validate.mjs --series=polish
npm run render -- --series=polish
# 成本主题（设计目标，非节省比例）：
node validate.mjs --series=cost
npm run render -- --series=cost
# 成本预算版（相对全程 Astra，非实测）：
node validate.mjs --series=cost-budget
npm run render -- --series=cost-budget
# 编辑新版动效：
npm run studio:polish
```

可用 `LIVECANVAS_BROWSER` 指定 Chromium 可执行文件。渲染器只创建独立浏览器实例，不读取用户浏览器账号。
`npm run render -- --stills` 只渲染封面/抽帧，`--only=roles-zh` 等只制作指定版本。
原版封面是第 126 帧 / 4.2 秒；视频 1200×676、30 fps、5 秒。
新版封面是第 156 帧 / 5.2 秒；视频 1600×900、30 fps、6 秒。
两套视频均为无声 H.264/yuv420p BT.709，PNG 原图按比例完整显示，不拉伸或裁切。
GIF 为 960 像素宽的循环网页预览。所有移动都由 `useCurrentFrame()` 决定。
Remotion 自带的 FFmpeg 缺少 `fps` / `select` 滤镜，本工程使用输出帧率与时间定位，不依赖系统 FFmpeg。
视频采用无损 PNG 中间帧，避免 JPEG 中间帧造成文字和色彩的额外损失。

`validate.mjs` 保留指定 Git 提交的来源快照。Skill 与角色配置仍要求当前文件完全一致；README 和成本说明允许排版与补充内容，但每条引用都必须同时存在于历史快照和当前文档，且分别记录 SHA-256。新版预算由费率摘录与算式单独检查；根目录文档测试检查当前模型、费率、图片和链接。后续若模型或策略改变，需要先更新事实基线，不能把旧图自动当作新版说明。

## Live Photo（macOS 可选交付）

原始 LiveCanvas 工具与完整 MIT 许可均保留。编译后，针对不存在的 `live/` 输出目录执行一次：

```sh
mkdir -p .build
swiftc -swift-version 5 tools/pair_live_photo.swift -o .build/pair-live-photo
node package-live.mjs
# 新版：
node package-live.mjs --series=polish
node package-live.mjs --series=cost
node package-live.mjs --series=cost-budget
```

已有包不应直接覆盖。需要重新生成时先保留旧版输出，避免混用不同渲染的 JPG/MOV。
`.pvt.zip` 解压后得到实况资源包；它不是一个普通视频，也不能保证在 iPhone「文件」App 中直接预览。
本机 `PHLivePhoto.request` 加载不等于手机播放、相册导入或锁屏验证。不会自动打开照片 App 或写入图库。

## 验收与许可

`tools/verify-images.py` 需要 Pillow，只读比较图片和 GIF，写入 QA 记录，不处理或编辑图片。
`tools/verify-preview.mjs` 使用 Playwright，可通过 `LIVECANVAS_PLAYWRIGHT` 指定已有模块路径，检查 loopback 预览。

```sh
python3 tools/verify-images.py
python3 tools/verify-images.py --series=polish
python3 tools/review-polish.py
python3 tools/verify-images.py --series=cost
python3 tools/review-polish.py --series=cost
python3 tools/verify-images.py --series=cost-budget
python3 tools/review-polish.py --series=cost-budget
python3 -m http.server 8769 --bind 127.0.0.1
# 另一个终端；必须使用实际启动的端口：
node tools/verify-preview.mjs http://127.0.0.1:8769/preview.html
```

机器校验不能替代事实核实与画面检查。发布到 README 前应查看实际封面、抽帧和动效。
新版实物画面比较见 [design-qa.md](design-qa.md)；逐项验收范围见 [QA-polish.md](QA-polish.md)。
补充成本图的事实边界与检查范围见 [sources-cost.md](sources-cost.md) 和 [QA-cost.md](QA-cost.md)。
当前项目事实范围与许可详见 [sources.md](sources.md) 和 [sources-polish.md](sources-polish.md)；LiveCanvas 为 MIT，Remotion 使用其自身许可。
预算版计算与验收见 [sources-cost-budget.md](sources-cost-budget.md) 和 [QA-cost-budget.md](QA-cost-budget.md)。
中英文 README 接入、文档测试与本地浏览器检查见 [QA-readme-integration.md](QA-readme-integration.md)。
没有复制上游演示媒体、第三方厂商标识或社交平台素材；预算数字经过算式验证，不冒充成本/速度实测。
