# 事实与素材来源

截止日：2026-10-01，Asia/Shanghai。项目事实对应 `f4dba1c20b0dc299fbcf565bc883c5afdc0324a9`，不是后续版本承诺。

- [候选 README](https://github.com/yehyakin/codex-prove/blob/f4dba1c20b0dc299fbcf565bc883c5afdc0324a9/README.md)：Direct / Solo / Assist / Coordinated 的含义与按需分工。
- [Sol 执行配置](https://github.com/yehyakin/codex-prove/blob/f4dba1c20b0dc299fbcf565bc883c5afdc0324a9/.codex/agents/prove-complex-worker.toml)：`gpt-6.1-sol/high`，同一上下文完成规划、实现与检查。
- [Astra 配置](https://github.com/yehyakin/codex-prove/blob/f4dba1c20b0dc299fbcf565bc883c5afdc0324a9/.codex/agents/prove-specialist-worker.toml)：`gpt-6-astra/high`，具体难题/独立评审，操作上保持只读，不承诺 OS 隔离。
- [Luna 配置](https://github.com/yehyakin/codex-prove/blob/f4dba1c20b0dc299fbcf565bc883c5afdc0324a9/.codex/agents/prove-efficient-worker.toml)：`gpt-6-luna/max`，规则明确且可检查的机械批量。
- [控制者配置](https://github.com/yehyakin/codex-prove/blob/f4dba1c20b0dc299fbcf565bc883c5afdc0324a9/.codex/agents/prove-controller.toml)：与执行者同为 Sol，保留四个角色 ID，但不要求全部启动。

原始摘录、完整提交文件快照与 SHA-256 由 `node validate.mjs` 保存至 `out/source-evidence.json`；同时校验当前事实文件未偏离该提交。
`data.json` 中六条 claim 分别引用来源。这里不使用时间序列、不做指标比较，因此不调用 LiveCanvas 的时间序列校验器。
画面中的文件数量、路径长度、移动速度均为流程示意。没有成本、速度、吞吐或模型综合能力的测试结论。
中英文版本是同一事实的翻译，不计作不同内容主题。

## LiveCanvas 与许可

使用用户指定的 [pengchujin/livecanvas](https://github.com/pengchujin/livecanvas/tree/8b6ca254b9536025945d0a1a4cf932ba4c905a0a/livecanvas)，按内容核实、分镜、同源封面、帧驱动动画、逐项验收的流程制作。
模板和配对/封装工具以 MIT 提供，版权声明保留在 `licenses/LiveCanvas-MIT.txt`。
Remotion 使用 [Remotion License](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)，本项目没有购买、声称购买或绕过任何授权。正式用于不满足免费条件的机构时需自行确认公司许可。
未复制 LiveCanvas 演示作品、Google/OpenAI 标志、Twemoji 或第三方图片。原创示意图记录于 `assets.json`。

## 验收边界

静态封面取同一 composition 的第 126 帧；30 fps 下对应 4.2 秒，位于最终停留段。
GIF/MP4 是预览，不是原生 Live Photo。Live Photo 如生成，将分别校验配对标识、timed metadata、本机 PHLivePhoto 加载与包内哈希。
不自动启动照片 App、不导入相册、不请求照片库权限；iPhone、锁屏、社交平台播放均不作验收承诺。
