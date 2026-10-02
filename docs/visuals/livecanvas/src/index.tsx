import React, {type CSSProperties, type ReactNode} from 'react';
import {AbsoluteFill, Composition, Easing, interpolate, registerRoot, useCurrentFrame} from 'remotion';

type Locale = 'zh' | 'en';
type Scene = 'roles' | 'solo';
type Props = {locale: Locale; scene: Scene};
const C = {bg: '#0B111E', panel: '#121D30', ink: '#F3F3EB', muted: '#A6B2C7', orange: '#FF9364', violet: '#B4AAFF', mint: '#8DDBBF', line: '#344158'};
const font = "-apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', Arial, sans-serif";
const mono = "'SFMono-Regular', Menlo, Consolas, monospace";
const ease = Easing.bezier(0.23, 1, 0.32, 1);
const p = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
const linear = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
const cubic = (t: number, a: number, b: number, c: number, d: number) => (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d;

function Box({x, y, w, h, style, children}: {x: number; y: number; w?: number; h?: number; style?: CSSProperties; children?: ReactNode}) {
  return <div style={{position: 'absolute', left: x, top: y, width: w, height: h, boxSizing: 'border-box', ...style}}>{children}</div>;
}

function Icon({kind, color = C.ink, size = 32}: {kind: 'sol' | 'astra' | 'luna' | 'file' | 'plan' | 'code' | 'check'; color?: string; size?: number}) {
  return <svg width={size} height={size} viewBox="0 0 40 40" fill="none" aria-hidden="true"><g stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {kind === 'sol' && <><circle cx="20" cy="20" r="7" fill={color} fillOpacity=".16"/>{[0,45,90,135,180,225,270,315].map(a => <path key={a} d="M20 3V7" transform={`rotate(${a} 20 20)`}/>)}</>}
    {kind === 'astra' && <path d="M20 4L24 16L36 20L24 24L20 36L16 24L4 20L16 16Z" fill={color} fillOpacity=".13"/>}
    {kind === 'luna' && <path d="M29 30A15 15 0 0 1 16 4A15 15 0 1 0 35 24A15 15 0 0 1 29 30Z" fill={color} fillOpacity=".13"/>}
    {kind === 'file' && <><path d="M11 5H24L31 12V35H11Z"/><path d="M24 5V13H31M16 20H25M16 26H25"/></>}
    {kind === 'plan' && <><path d="M13 10H32M13 20H32M13 30H26M6 10H7M6 20H7M6 30H7"/></>}
    {kind === 'code' && <path d="M12 11L4 20L12 29M28 11L36 20L28 29M23 7L17 33"/>}
    {kind === 'check' && <><circle cx="20" cy="20" r="15"/><path d="M12 20L18 26L28 14"/></>}
  </g></svg>;
}

function Chrome({locale, scene}: Props) {
  return <>
    <AbsoluteFill style={{background: C.bg}}/>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 82% 35%, #1A253D 0%, transparent 57%)'}}/>
    <svg width="1200" height="675" style={{position: 'absolute'}}><path d="M56 97H1144M56 617H1144" stroke={C.line} strokeOpacity=".65"/><path d="M56 97H148" stroke={C.orange} strokeWidth="2"/></svg>
    <Box x={56} y={44} style={{display: 'flex', gap: 12, alignItems: 'center'}}>
      <div style={{width: 26, height: 26, border: `1.5px solid ${C.orange}`, borderRadius: 7, display: 'flex', alignItems: 'center', justifyContent: 'center'}}><span style={{fontFamily: mono, fontWeight: 700, fontSize: 18, color: C.orange}}>P</span></div>
      <span style={{fontFamily: mono, fontSize: 23, letterSpacing: 1.8, fontWeight: 600}}>CODEX PROVE</span>
    </Box>
    <Box x={800} y={49} w={344} style={{fontSize: 15, textAlign: 'right', color: C.muted, letterSpacing: .4}}>{locale === 'zh' ? (scene === 'roles' ? '模型分工 · 候选方案' : '完整任务 · 候选方案') : (scene === 'roles' ? 'MODEL ROLES · CANDIDATE' : 'COMPLETE TASK · CANDIDATE')}</Box>
    <Box x={56} y={636} style={{fontSize: 13, color: C.muted}}>{locale === 'zh' ? '工作流示意 · 不代表耗时或性能' : 'Workflow illustration · not timing or performance data'}</Box>
    <Box x={846} y={635} w={298} style={{fontFamily: mono, fontSize: 13, textAlign: 'right', color: C.muted}}>yehyakin/codex-prove</Box>
  </>;
}

function FileTile({x, y, label, opacity = 1, scale = 1}: {x: number; y: number; label: string; opacity?: number; scale?: number}) {
  return <Box x={x} y={y} w={85} h={108} style={{opacity, transform: `scale(${scale})`, transformOrigin: 'center', background: '#E9EBDD', color: C.bg, borderRadius: 11, boxShadow: '0 12px 30px #00000033', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 7}}><Icon kind="file" color={C.bg} size={37}/><span style={{fontSize: 16, fontWeight: 600}}>{label}</span></Box>;
}

function RoleCard({x, y, name, model, label, kind, accent, progress}: {x: number; y: number; name: string; model: string; label: string; kind: 'astra' | 'luna'; accent: string; progress: number}) {
  return <Box x={x} y={y} w={258} h={143} style={{padding: '22px 23px', borderRadius: 19, background: C.panel, border: `1px solid ${accent}66`, opacity: .28+.72*progress, transform: `translateY(${(1-progress)*12}px)`, boxShadow: '0 10px 24px #00000022'}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 10, marginBottom: 9}}><Icon kind={kind} color={accent} size={30}/><span style={{fontSize: 25, color: accent, fontWeight: 650, letterSpacing: .5}}>{name}</span></div>
    <div style={{fontSize: 20, fontWeight: 550, marginBottom: 8}}>{label}</div><div style={{fontFamily: mono, fontSize: 14, color: C.muted}}>{model}</div>
  </Box>;
}

function Roles({locale}: {locale: Locale}) {
  const f = useCurrentFrame();
  const branch = p(f, 43, 71);
  const incoming = linear(f, 14, 41);
  const returning = linear(f, 80, 103);
  const zh = locale === 'zh';
  return <>
    <Box x={56} y={146} style={{color: C.orange, fontFamily: mono, fontSize: 16, letterSpacing: 1}}>GPT-6.1 SOL · HIGH</Box>
    <Box x={53} y={191} w={475} style={{fontSize: zh ? 53 : 56, lineHeight: 1.2, fontWeight: 650, letterSpacing: zh ? -1.6 : -2}}>{zh ? <>Sol 执行<br/>完整任务。</> : <>Sol owns<br/>the whole task.</>}</Box>
    <Box x={56} y={366} w={445} style={{fontSize: zh ? 24 : 22, lineHeight: 1.7, color: C.muted}}>{zh ? <>Astra 专项分析。<br/>Luna 机械批量。</> : <>Astra for focused analysis.<br/>Luna for mechanical batches.</>}</Box>
    <Box x={56} y={503} w={431} style={{borderLeft: `2px solid ${C.orange}`, paddingLeft: 19, fontSize: zh ? 19 : 18, lineHeight: 1.6}}>{zh ? <>先让一个 Sol 做完。<br/><span style={{color: C.muted}}>有独立工作，再按需分工。</span></> : <>Start with one Sol.<br/><span style={{color: C.muted}}>Delegate useful, independent work.</span></>}</Box>
    <svg width="1200" height="675" style={{position: 'absolute'}}>
      <defs><marker id="role-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke={C.orange} strokeWidth="1.5"/></marker></defs>
      <path d="M639 236H685" stroke={C.line} strokeWidth="2"/><path d="M639 236H685" stroke={C.orange} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1-p(f, 12, 41)} markerEnd="url(#role-arrow)"/>
      {['M815 329C815 375 702 366 702 426', 'M952 329C952 375 995 367 995 426'].map((d, i) => <React.Fragment key={d}>
        <path d={d} fill="none" stroke={C.line} strokeWidth="2" strokeDasharray="5 6"/><path d={d} fill="none" stroke={C.orange} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1-branch} opacity={.72}/>
        <path d={i === 0 ? 'M677 426C677 366 778 355 778 329' : 'M1020 426C1020 370 991 360 991 329'} fill="none" stroke={i === 0 ? C.violet : C.mint} strokeWidth="1.5" strokeDasharray="3 6" opacity={p(f, 70, 90)*.7}/>
      </React.Fragment>)}
      {incoming > 0 && incoming < 1 && <g transform={`translate(${642+36*incoming} 236)`}><rect x="-6" y="-8" width="12" height="16" rx="3" fill={C.orange}/></g>}
      {returning > 0 && returning < 1 && <><circle cx={cubic(returning, 677, 677, 778, 778)} cy={cubic(returning, 426, 366, 355, 329)} r="4" fill={C.violet}/><circle cx={cubic(returning, 1020, 1020, 991, 991)} cy={cubic(returning, 426, 370, 360, 329)} r="4" fill={C.mint}/></>}
    </svg>
    <FileTile x={554} y={183} label={zh ? '任务' : 'TASK'} scale={.96+.04*p(f, 0, 15)}/>
    <Box x={693} y={162} w={414} h={167} style={{background: 'linear-gradient(125deg, #2C2727, #182033 74%)', border: `1px solid ${C.orange}B3`, borderRadius: 23, padding: '26px 29px', boxShadow: '0 14px 40px #00000033'}}>
      <div style={{display: 'flex', gap: 14, alignItems: 'center'}}><Icon kind="sol" color={C.orange} size={43}/><span style={{fontSize: 34, fontWeight: 650, color: C.orange, letterSpacing: .7}}>SOL</span><span style={{marginLeft: 'auto', fontFamily: mono, fontSize: 14, color: C.muted}}>6.1 / high</span></div>
      <div style={{marginTop: 20, fontSize: zh ? 23 : 22, letterSpacing: .5}}>{zh ? '规划 → 实现 → 检查' : 'Plan → Build → Verify'}</div>
    </Box>
    <Box x={836} y={360} w={117} h={37} style={{border: `1px solid ${C.line}`, borderRadius: 20, background: C.bg, color: C.muted, fontSize: 15, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>{zh ? '仅按需' : 'IF NEEDED'}</Box>
    <RoleCard x={573} y={426} name="ASTRA" model="GPT-6 · high" label={zh ? '只读分析' : 'Read-only analysis'} kind="astra" accent={C.violet} progress={branch}/>
    <RoleCard x={864} y={426} name="LUNA" model="GPT-6 · max" label={zh ? '机械批量' : 'Mechanical batches'} kind="luna" accent={C.mint} progress={branch}/>
  </>;
}

function Solo({locale}: {locale: Locale}) {
  const f = useCurrentFrame();
  const zh = locale === 'zh';
  const starts = [15, 38, 61, 82];
  const pathSegments = [[181, 232], [440, 477], [685, 722], [930, 977]];
  const labels = zh ? ['规划', '实现', '验证'] : ['Plan', 'Build', 'Verify'];
  const hints = zh ? ['理解目标与边界', '完成代码与修改', '检查文件与测试'] : ['Goal and constraints', 'Code and changes', 'Files and tests'];
  const kinds = ['plan', 'code', 'check'] as const;
  return <>
    <Box x={56} y={139} w={1088} style={{fontSize: zh ? 46 : 50, fontWeight: 650, letterSpacing: zh ? -1.5 : -1.8, lineHeight: 1.2}}>{zh ? <>完整任务，先由一个 <span style={{color: C.orange}}>Sol</span> 做完。</> : <>One task. One <span style={{color: C.orange}}>Sol</span> context.</>}</Box>
    <Box x={57} y={211} w={1087} style={{fontSize: 22, color: C.muted}}>{zh ? '规划、实现、验证，不必拆成三次代理交接。' : 'Plan, build and verify without three separate agent handoffs.'}</Box>
    <Box x={56} y={288} w={1088} h={227} style={{background: '#111B2B', border: `1px solid ${C.orange}80`, borderRadius: 23}}/>
    <Box x={84} y={270} w={zh ? 298 : 320} h={36} style={{background: C.bg, padding: '8px 15px', display: 'flex', alignItems: 'center', gap: 10, fontFamily: mono, fontSize: 15, color: C.orange}}><Icon kind="sol" size={23} color={C.orange}/>{zh ? '同一上下文 · SOL 6.1' : 'ONE CONTEXT · SOL 6.1'}</Box>
    <svg width="1200" height="675" style={{position: 'absolute'}}>{pathSegments.map(([x1, x2], i) => <React.Fragment key={x1}>
      <path d={`M${x1} 412H${x2}`} stroke={C.line} strokeWidth="2"/><path d={`M${x1} 412H${x2}`} stroke={C.orange} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1-p(f, starts[i], starts[i]+17)}/>
      <path d={`M${x2-5} 408L${x2} 412L${x2-5} 416`} fill="none" stroke={C.orange} strokeWidth="1.5" opacity={p(f, starts[i]+9, starts[i]+17)}/>
      {f > starts[i] && f < starts[i]+17 && <rect x={x1+(x2-x1)*linear(f, starts[i], starts[i]+17)-4} y="405" width="8" height="14" rx="3" fill={C.orange}/>}
    </React.Fragment>)}</svg>
    <FileTile x={94} y={359} label={zh ? '任务' : 'TASK'} opacity={.65+.35*p(f, 0, 12)}/>
    {[236, 481, 726].map((x, i) => {
      const done = p(f, starts[i]+10, starts[i]+25);
      return <Box key={x} x={x} y={342} w={204} h={137} style={{borderRadius: 15, background: '#19243A', border: `1px solid ${i === 2 ? C.mint : C.orange}${done > .9 ? '80' : '18'}`, padding: '19px 20px', opacity: .55+.45*done}}>
        <div style={{display: 'flex', gap: 13, alignItems: 'center'}}><Icon kind={kinds[i]} color={i === 2 ? C.mint : C.orange} size={34}/><span style={{fontSize: 27, fontWeight: 550}}>{labels[i]}</span></div><div style={{marginTop: 18, fontSize: zh ? 17 : 15, color: C.muted}}>{hints[i]}</div>
      </Box>;
    })}
    <Box x={982} y={368} w={129} h={91} style={{borderRadius: 16, background: C.mint, color: C.bg, display: 'flex', alignItems: 'center', flexDirection: 'column', justifyContent: 'center', gap: 5, opacity: .3+.7*p(f, 94, 108), transform: `scale(${.96+.04*p(f, 94, 108)})`}}><Icon kind="check" color={C.bg} size={30}/><span style={{fontSize: 17, fontWeight: 650}}>{zh ? '交付结果' : 'DELIVER'}</span></Box>
    {[
      {x: 56, title: zh ? '小任务 · Direct' : 'Small task · Direct', detail: zh ? '当前 Codex 直接完成' : 'The current Codex handles it'},
      {x: 433, title: zh ? '只分析 · Assist' : 'Analysis only · Assist', detail: zh ? '不改代码，Astra 按需加入' : 'No edits; Astra only if useful'},
      {x: 810, title: zh ? '独立工作 · Coordinated' : 'Independent work · Coordinated', detail: zh ? '值得并行时，再明确分工' : 'Delegate when parallel work helps'},
    ].map(item => <Box key={item.x} x={item.x} y={543} w={334} style={{borderLeft: `1px solid ${C.line}`, paddingLeft: 17}}><div style={{fontSize: zh ? 17 : 15.5, fontWeight: 550, marginBottom: 8}}>{item.title}</div><div style={{fontSize: zh ? 15 : 14, color: C.muted}}>{item.detail}</div></Box>)}
  </>;
}

export function Artwork({locale, scene}: Props) {
  return <AbsoluteFill style={{fontFamily: font, color: C.ink, overflow: 'hidden'}}><Chrome locale={locale} scene={scene}/>{scene === 'roles' ? <Roles locale={locale}/> : <Solo locale={locale}/>}</AbsoluteFill>;
}
function Root() {
  return <>{(['roles', 'solo'] as const).flatMap(scene => (['zh', 'en'] as const).map(locale => <Composition key={`${scene}-${locale}`} id={`${scene}-${locale}`} component={Artwork} defaultProps={{scene, locale}} width={1200} height={676} fps={30} durationInFrames={150}/>))}</>;
}
registerRoot(Root);
