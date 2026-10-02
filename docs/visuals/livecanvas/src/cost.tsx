import React, {type CSSProperties} from 'react';
import {AbsoluteFill, Composition, Easing, Img, interpolate, registerRoot, staticFile, useCurrentFrame} from 'remotion';

type Locale = 'zh' | 'en';
type Area = readonly [left: number, top: number, right: number, bottom: number];
const ease = Easing.bezier(0.23, 1, 0.32, 1);

// Exposure over the real generated image; no replacement drawing or measured amount.
function PathExposure({area, start, end}: {area: Area; start: number; end: number}) {
  const frame = useCurrentFrame();
  const value = interpolate(frame, [start, end], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (value === 1) return null;
  const [left, top, right, bottom] = area;
  const edge = -10 + value * 120;
  const region: CSSProperties = {position: 'absolute', left: `${left}%`, top: `${top}%`, width: `${right-left}%`, height: `${bottom-top}%`, maskImage: 'radial-gradient(ellipse closest-side, black 32%, transparent 100%)'};
  return <div style={region}><AbsoluteFill style={{background: '#02050D', opacity: .65, maskImage: `linear-gradient(to right, transparent ${edge}%, black ${edge+10}%)`}}/></div>;
}

function CostArtwork({locale}: {locale: Locale}) {
  return <AbsoluteFill style={{background: '#0B111E'}}>
    <Img src={staticFile(`media/cost/cost-${locale}.png`)} style={{width: '100%', height: '100%', objectFit: 'contain'}}/>
    <PathExposure area={[43, 30, 93, 39.5]} start={8} end={72}/>
    <PathExposure area={[46, 57.4, 73, 61.8]} start={72} end={108}/>
    <PathExposure area={[46, 63, 73, 73.4]} start={72} end={108}/>
  </AbsoluteFill>;
}

function Root() {
  return <>{(['zh', 'en'] as const).map(locale => <Composition key={locale} id={`cost-${locale}`} component={CostArtwork} defaultProps={{locale}} width={1600} height={900} fps={30} durationInFrames={180}/>)}</>;
}
registerRoot(Root);
