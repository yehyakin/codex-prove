import React, {type CSSProperties} from 'react';
import {AbsoluteFill, Composition, Easing, Img, interpolate, registerRoot, staticFile, useCurrentFrame} from 'remotion';

type Locale = 'zh' | 'en';
type Area = readonly [left: number, top: number, right: number, bottom: number];
const ease = Easing.bezier(0.23, 1, 0.32, 1);
const artwork = {
  zh: <Img src={staticFile('media/cost-budget/cost-budget-zh.png')} style={{width: '100%', height: '100%', objectFit: 'contain'}}/>,
  en: <Img src={staticFile('media/cost-budget/cost-budget-en.png')} style={{width: '100%', height: '100%', objectFit: 'contain'}}/>,
};

// Emphasize the comparison connections, never animate the figures or qualifiers.
function ComparisonExposure({area, start, end}: {area: Area; start: number; end: number}) {
  const frame = useCurrentFrame();
  const value = interpolate(frame, [start, end], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (value === 1) return null;
  const [left, top, right, bottom] = area;
  const edge = -10 + value * 120;
  const region: CSSProperties = {position: 'absolute', left: `${left}%`, top: `${top}%`, width: `${right-left}%`, height: `${bottom-top}%`, maskImage: 'radial-gradient(ellipse closest-side, black 32%, transparent 100%)'};
  return <div style={region}><AbsoluteFill style={{background: '#02050D', opacity: .75, maskImage: `linear-gradient(to right, transparent ${edge}%, black ${edge+10}%)`}}/></div>;
}

function BudgetArtwork({locale}: {locale: Locale}) {
  return <AbsoluteFill style={{background: '#0B111E'}}>
    {artwork[locale]}
    <ComparisonExposure area={[43, 28.5, 52.4, 39]} start={8} end={48}/>
    <ComparisonExposure area={[43, 39, 52.4, 60]} start={48} end={108}/>
  </AbsoluteFill>;
}

function Root() {
  return <>{(['zh', 'en'] as const).map(locale => <Composition key={locale} id={`cost-budget-${locale}`} component={BudgetArtwork} defaultProps={{locale}} width={1600} height={900} fps={30} durationInFrames={180}/>)}</>;
}
registerRoot(Root);
