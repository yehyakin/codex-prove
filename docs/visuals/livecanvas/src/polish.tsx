import React, {type CSSProperties} from 'react';
import {AbsoluteFill, Composition, Easing, Img, interpolate, registerRoot, staticFile, useCurrentFrame} from 'remotion';

type Locale = 'zh' | 'en';
type Scene = 'routing' | 'ownership' | 'evidence';
type Props = {scene: Scene; locale: Locale};
type Area = readonly [left: number, top: number, right: number, bottom: number];
const ease = Easing.bezier(0.23, 1, 0.32, 1);
const progress = (frame: number, start: number, end: number) => interpolate(frame, [start, end], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

/** A soft exposure mask over the real PNG, never a replacement drawing.
 * All type, icons, paths and texture remain in the selected/generated artwork.
 * A complete frame is the unaltered source image, with contain sizing.
 */
function Reveal({area, start, end}: {area: Area; start: number; end: number}) {
  const frame = useCurrentFrame();
  const value = progress(frame, start, end);
  if (value === 1) return null;
  const [left, top, right, bottom] = area;
  const edge = -10 + value * 120;
  const feather = 'radial-gradient(ellipse closest-side, black 32%, transparent 100%)';
  const region: CSSProperties = {position: 'absolute', left: `${left}%`, top: `${top}%`, width: `${right-left}%`, height: `${bottom-top}%`, maskImage: feather};
  return <div style={region}><AbsoluteFill style={{background: '#02050D', opacity: .65, maskImage: `linear-gradient(to right, transparent ${edge}%, black ${edge+10}%)`}}/></div>;
}

export function PolishedArtwork({scene, locale}: Props) {
  return <AbsoluteFill style={{background: '#0B111E'}}>
    <Img src={staticFile(`media/polish/${scene}-${locale}.png`)} style={{width: '100%', height: '100%', objectFit: 'contain'}}/>
    {scene === 'routing' ? <Reveal area={[31, 16, 97, 86]} start={8} end={103}/> : null}
    {scene === 'ownership' ? <>
      <Reveal area={[40.5, 18, 97, 41]} start={8} end={58}/>
      <Reveal area={[40.5, 42, 97, 65]} start={8} end={58}/>
      <Reveal area={[4, 72, 97, 85]} start={58} end={126}/>
    </> : null}
    {scene === 'evidence' ? <Reveal area={[40, 17, 97, 71]} start={8} end={103}/> : null}
  </AbsoluteFill>;
}

function Root() {
  return <>{(['routing', 'ownership', 'evidence'] as const).flatMap(scene => (['zh', 'en'] as const).map(locale => <Composition key={`${scene}-${locale}`} id={`${scene}-${locale}`} component={PolishedArtwork} defaultProps={{scene, locale}} width={1600} height={900} fps={30} durationInFrames={180}/>))}</>;
}
registerRoot(Root);
