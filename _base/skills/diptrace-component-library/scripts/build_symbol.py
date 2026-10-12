"""Native vector-font DipTrace symbol from a reviewed JSON spec; stdlib only."""
import argparse,csv,hashlib,json,math,re
from pathlib import Path
import xml.etree.ElementTree as ET

TYPES={'Undefined','Passive','Input','Output','Bidirectional','Open High','Open Low','Passive High','Passive Low','3 State','Power'}

def label(pin,policy):
    tokens=pin['name'].split('/')
    for key in ['aliases','configuration']:
        values=pin.get(key,[])
        if isinstance(values,str):values=values.split('/')
        tokens.extend(v for v in values if v and str(v).lower() not in {'none','n/a'})
    drop=policy.get('omit_alias_regex')
    tokens=[v for i,v in enumerate(tokens) if i==0 or not(drop and re.fullmatch(drop,v))]
    lvds=pin.get('lvds',False)
    if policy.get('include_lvds',True) and (lvds is True or str(lvds).lower()=='true'):tokens.append('LVDS')
    dq=pin.get('dqs','')
    if policy.get('include_dqs',True) and dq and str(dq).lower() not in {'none','n/a'}:tokens.append(dq)
    tokens=list(dict.fromkeys(tokens))
    if policy.get('append_ball',True):tokens.append(str(pin['ball']))
    return '/'.join(tokens)

def element(parent,tag,text=None,**attrs):
    child=ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})
    if text is not None:child.text=str(text)
    return child

def build(spec,output):
    source={str(p['ball']):p for p in spec['pins']}
    if len(source)!=len(spec['pins']):raise ValueError('Duplicate physical contact in source')
    if not source or not spec['parts']:raise ValueError('Empty component')
    used=[str(p['ball']) for part in spec['parts'] for p in part['pins']]
    if len(used)!=len(set(used)) or set(used)!=set(source):raise ValueError('Missing/duplicate/unknown placed contacts')
    if any(p['type'] not in TYPES for p in source.values()):raise ValueError('Unknown electrical type')
    policy=spec.get('label_policy',{})
    root=ET.Element('Library',Type='DipTrace-ComponentLibrary',Name=spec['name'],Hint=spec.get('hint',spec['name']),Version='5.3.5.1',Units='mm')
    element(root,'Library',Type='DipTrace-PatternLibrary',Units='mm')
    comp=element(element(root,'Components'),'Component',Id=0)
    for part_id,layout in enumerate(spec['parts']):
        w,h=float(layout['width']),float(layout['height'])
        if min(w,h)<=0:raise ValueError('Invalid body dimensions')
        part=element(comp,'Part',Id=part_id,PartType='Normal',Type='Free',Int1=0,Int2=0,Width=w,Height=h,LockTypeChange='Y',ShowNumbers='Hide' if policy.get('append_ball',True) else 'Show')
        if part_id==0:
            part.set('RefDes',spec.get('refdes','D'))
            for tag,key in [('Name','name'),('Manufacturer','manufacturer'),('Datasheet','datasheet')]:
                if spec.get(key):element(part,tag,spec[key])
        element(part,'PartName',layout.get('name',f'Part {part_id+1}'))
        element(part,'Value',layout.get('value',''));element(part,'Origin',X=0,Y=0)
        pins=element(part,'Pins')
        positions=set()
        for i,place in enumerate(layout['pins']):
            pin=source[str(place['ball'])];x,y=float(place['x']),float(place['y'])
            side=place['side']
            if side not in {'left','right'}:raise ValueError('Only left/right pins supported')
            if abs(abs(x)-w/2)>1e-5 or abs(y)>=h/2:raise ValueError('Pin is not on its body edge')
            if (x,y) in positions:raise ValueError('Coincident pins')
            positions.add((x,y))
            length=float(place.get('length',layout.get('pin_length',3.81)))
            size=float(place.get('font',layout.get('pin_font',5)))
            scale=float(place.get('name_scale',1))
            if min(length,size,scale)<=0:raise ValueError('Nonpositive pin/font dimension')
            p=element(pins,'Pin',Id=i,X=x,Y=y,Locked='N',Type='Default',ElectricType=pin['type'],Orientation=0 if side=='left' else 180,PadId=-1,Length=length,ShowName='Y',NumXShift=0,NumYShift=0,NameXShift=0,NameYShift=0,SignalDelay=0,NumOrientation=0,NameOrientation=0)
            element(p,'Name',label(pin,policy));element(p,'PadNumber',place['ball'])
            element(p,'NameFont',Size=round(size),FontSizeFloat=size,Width=-2,Scale=scale,FontMono='N')
        shapes=element(part,'Shapes')
        def shape(kind,points,**attrs):
            s=element(shapes,'Shape',Id=len(shapes),Type=kind,**attrs)
            for x,y in points:element(element(s,'Points') if s.find('Points') is None else s.find('Points'),'Point',X=x,Y=y)
            return s
        shape('Rectangle',[(-w/2,-h/2),(w/2,h/2)],LineWidth=layout.get('line_width',.25))
        for line in layout.get('lines',[]):
            if len(line)!=4:raise ValueError('Line requires four coordinates')
            shape('Line',[(line[0],line[1]),(line[2],line[3])],LineWidth=layout.get('line_width',.25))
        texts=list(layout.get('texts',[]))
        if layout.get('markings',True):
            texts.extend([dict(text=spec['name'],show='Name',x=0,y=h/2+5.08,size=9),dict(text=spec.get('refdes','D'),show='RefDes',x=-w/2,y=h/2+5.08,size=9,align='Left')])
        for t in texts:
            size=float(t.get('size',7))
            s=shape('Text',[(t['x'],t['y'])],FontVector='Y',FontMono='N',FontName='',FontSize=round(size),FontSizeFloat=size,FontColor=t.get('color',8388608),TextShow=t.get('show','Any Text'),FontWidth=-2,FontScale=t.get('scale',1),Angle=0,HorzAlign=t.get('align','Center'),VertAlign=t.get('valign','Center'),TextAlign=t.get('align','Center'),LineSpacing=1.2)
            element(element(s,'TextLines'),'TextLine',t.get('text',''))
        element(part,'Groups')
    ET.indent(root)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_suffix(output.suffix+'.tmp')
    ET.ElementTree(root).write(temporary,encoding='utf-8',xml_declaration=True)
    actual=ET.parse(temporary).getroot()
    emitted=actual.findall('.//Pin')
    if {p.findtext('PadNumber'):p.findtext('Name') for p in emitted}!={b:label(p,policy) for b,p in source.items()}:raise ValueError('Emitted pin mapping changed')
    texts=actual.findall('.//Shape[@Type="Text"]')
    if any(t.get('FontVector')!='Y' or t.get('FontName') for t in texts):raise ValueError('Unexpected TrueType text')
    temporary.replace(output)
    mapping=output.with_suffix('.pins.csv')
    with mapping.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['Ball','Visible label','Full manufacturer name','Full source record'])
        for b,p in source.items():writer.writerow([b,label(p,policy),p['name'],json.dumps(p,ensure_ascii=False)])
    report={'name':spec['name'],'contacts':len(source),'parts':[{'name':p.get('name',f'Part {i+1}'),'contacts':len(p['pins']),'width_mm':p['width'],'height_mm':p['height']} for i,p in enumerate(spec['parts'])],'all_text_vector':True,'vector_text_shapes':len(texts),'no_missing_duplicate_contacts':True,'pattern_attached':False,'GUI_import_verified':False,'source':spec.get('source'),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
    output.with_suffix('.validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('spec',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();print(json.dumps(build(json.loads(args.spec.read_text(encoding='utf-8-sig')),args.output),ensure_ascii=True))
