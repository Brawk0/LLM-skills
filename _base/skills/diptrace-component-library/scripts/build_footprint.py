"""BGA/QFN KiCad land pattern with explicit PCB dimensions; stdlib only."""
import argparse,hashlib,json,re
from pathlib import Path

def contacts(spec):
    kind=spec['kind'];pads=[]
    if kind=='bga':
        rows=spec['rows'];cols=int(spec['columns']);pitch=float(spec['pitch']);size=float(spec['pad_diameter'])
        if len(rows)!=len(set(rows)) or cols<1 or min(pitch,size)<=0:raise ValueError('Invalid BGA grid')
        for i,row in enumerate(rows):
            for j in range(cols):pads.append(dict(number=f'{row}{j+1}',x=(j-(cols-1)/2)*pitch,y=(i-(len(rows)-1)/2)*pitch,width=size,height=size,shape='circle'))
    elif kind=='qfn':
        n=int(spec['pins_per_side']);pitch=float(spec['pitch']);length=float(spec['land_length']);width=float(spec['land_width']);off=float(spec['land_center_offset'])
        if n<1 or min(pitch,length,width,off)<=0:raise ValueError('Invalid QFN parameters')
        for i in range(n):
            t=(i-(n-1)/2)*pitch
            for number,x,y,w,h in [(i+1,-off,t,length,width),(n+i+1,t,off,width,length),(2*n+i+1,off,-t,length,width),(3*n+i+1,-t,-off,width,length)]:
                pads.append(dict(number=str(number),x=x,y=y,width=w,height=h,shape='rect'))
        if spec.get('ep'):
            ep=spec['ep'];pads.append(dict(number=str(ep.get('number','0')),x=0,y=0,width=ep['width'],height=ep['height'],shape='rect',ep=True))
    else:raise ValueError('Unsupported package kind')
    if len({p['number'] for p in pads})!=len(pads):raise ValueError('Duplicate pad identifiers')
    return pads

def build(spec,output):
    pads=contacts(spec);bw,bh=map(float,spec['body'])
    if min(bw,bh)<=0:raise ValueError('Invalid body dimensions')
    name=spec['name']
    if re.search(r'[\s()"]',name):raise ValueError('Name must be a simple KiCad token')
    lines=[f'(module {name} (layer F.Cu) (tedit 0)','  (attr smd)',f'  (descr {json.dumps(spec.get("land_pattern_status","reconstructed land pattern"))})',f'  (fp_text reference REF** (at 0 {-bh/2-2}) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))',f'  (fp_text value {name} (at 0 {bh/2+2}) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))']
    for x1,y1,x2,y2 in [(-bw/2,-bh/2,bw/2,-bh/2),(bw/2,-bh/2,bw/2,bh/2),(bw/2,bh/2,-bw/2,bh/2),(-bw/2,bh/2,-bw/2,-bh/2)]:
        lines.append(f'  (fp_line (start {x1:g} {y1:g}) (end {x2:g} {y2:g}) (layer F.Fab) (width 0.15))')
    lines.append(f'  (fp_circle (center {-bw/2-.5:g} {-bh/2-.5:g}) (end {-bw/2-.3:g} {-bh/2-.5:g}) (layer F.SilkS) (width 0.12))')
    for p in pads:
        layers='F.Cu F.Mask' if p.get('ep') and spec.get('paste_windows') else 'F.Cu F.Paste F.Mask'
        lines.append(f'  (pad {p["number"]} smd {p["shape"]} (at {p["x"]:.6f} {p["y"]:.6f}) (size {p["width"]:.6f} {p["height"]:.6f}) (layers {layers}))')
    for window in spec.get('paste_windows',[]):
        ep=spec.get('ep')
        if not ep:raise ValueError('Paste windows require an exposed pad')
        x,y,w,h=(float(window[k]) for k in ['x','y','width','height'])
        if min(w,h)<=0 or abs(x)+w/2>ep['width']/2 or abs(y)+h/2>ep['height']/2:raise ValueError('Paste aperture is outside exposed pad')
        pts=[(x-w/2,y-h/2),(x+w/2,y-h/2),(x+w/2,y+h/2),(x-w/2,y+h/2)]
        lines.append('  (fp_poly (pts '+' '.join(f'(xy {a:g} {b:g})' for a,b in pts)+') (layer F.Paste) (width 0))')
    lines.append(')');data='\n'.join(lines)+'\n'
    # Parse delivered pad records independently of the generated pad objects.
    actual=re.findall(r'\(pad (\S+) smd (\w+) \(at ([-\d.]+) ([-\d.]+)\) \(size ([\d.]+) ([\d.]+)\)',data)
    if len(actual)!=len(pads):raise ValueError('Output pad count changed')
    by_num={p['number']:p for p in pads}
    for num,shape,x,y,w,h in actual:
        p=by_num[num]
        if shape!=p['shape'] or any(abs(float(a)-p[k])>1e-6 for a,k in zip([x,y,w,h],['x','y','width','height'])):raise ValueError('Output pad geometry changed')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(data,encoding='utf-8')
    report={'contacts':len(pads),'pads':pads,'source':spec.get('source'),'land_pattern_status':spec.get('land_pattern_status','unspecified custom reconstruction'),'top_view_Y_down':True,'GUI_import_verified':False,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
    output.with_suffix('.validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('spec',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();print(json.dumps(build(json.loads(args.spec.read_text(encoding='utf-8-sig')),args.output)))
