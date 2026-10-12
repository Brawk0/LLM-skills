"""Simplified colored BGA/QFN STEP with reimport checks; requires CadQuery."""
import argparse,json,re
from pathlib import Path
import cadquery as cq
from cadquery.occ_impl.exporters.assembly import exportAssembly

def build(spec,output):
    w,h=map(float,spec['body']);height=float(spec['height']);kind=spec['kind']
    if min(w,h,height)<=0:raise ValueError('Invalid package envelope')
    contacts=[];positions=[]
    if kind=='bga':
        stand=float(spec['standoff']);diam=float(spec['ball_diameter']);pitch=float(spec['pitch']);rows=spec['rows'];cols=int(spec['columns'])
        if not rows or len(rows)!=len(set(rows)) or cols<1 or not 0<stand<height or min(diam,pitch)<=0:raise ValueError('Invalid BGA data')
        if (cols-1)*pitch+diam>w or (len(rows)-1)*pitch+diam>h:raise ValueError('Ball grid exceeds body envelope')
        matrix=cq.Matrix([[1,0,0,0],[0,1,0,0],[0,0,stand/diam,0],[0,0,0,1]])
        ball=cq.Workplane('XY').sphere(diam/2).val().transformGeometry(matrix)
        for i,row in enumerate(rows):
            for j in range(cols):
                x=(j-(cols-1)/2)*pitch;y=((len(rows)-1)/2-i)*pitch
                contacts.append(ball.translate((x,y,stand/2)));positions.append({'number':f'{row}{j+1}','x':x,'y':y})
        bottom=stand
    elif kind=='qfn':
        n=int(spec['pins_per_side']);pitch=float(spec['pitch']);length=float(spec['contact_length']);width=float(spec['contact_width']);thick=float(spec['contact_height']);off=float(spec['contact_center_offset'])
        bottom=float(spec.get('body_bottom',thick))
        if n<1 or min(pitch,length,width,thick,off)<=0 or not 0<=bottom<height or thick>=height:raise ValueError('Invalid QFN data')
        for i in range(n):
            t=((n-1)/2-i)*pitch
            # Cartesian Y up; equivalent to the footprint helper's top-view order.
            for num,x,y,a,b in [(i+1,-off,t,length,width),(n+i+1,-t,-off,width,length),(2*n+i+1,off,-t,length,width),(3*n+i+1,t,off,width,length)]:
                if abs(x)+a/2>w/2+1e-6 or abs(y)+b/2>h/2+1e-6:raise ValueError('Physical contact exceeds body envelope')
                contacts.append(cq.Solid.makeBox(a,b,thick,cq.Vector(x-a/2,y-b/2,0)));positions.append({'number':str(num),'x':x,'y':y})
        if spec.get('ep'):
            ep=spec['ep'];a,b,t=(float(ep[k]) for k in ['width','height','thickness'])
            if min(a,b,t)<=0 or a>w or b>h or t>=height:raise ValueError('Invalid physical exposed pad')
            contacts.append(cq.Solid.makeBox(a,b,t,cq.Vector(-a/2,-b/2,0)));positions.append({'number':str(ep.get('number','0')),'x':0,'y':0})
    else:raise ValueError('Unsupported model kind')
    body=cq.Solid.makeBox(w,h,height-bottom,cq.Vector(-w/2,-h/2,bottom))
    if kind=='qfn':body=body.cut(cq.Compound.makeCompound(contacts))
    marker=None
    if spec.get('marker'):
        m=spec['marker'];x,y,diam,depth=(float(m[k]) for k in ['x','y','diameter','depth'])
        if min(diam,depth)<=0 or depth>=height-bottom or abs(x)+diam/2>w/2 or abs(y)+diam/2>h/2:raise ValueError('Marker is outside body')
        marker=cq.Solid.makeCylinder(diam/2,depth,cq.Vector(x,y,height-depth));body=body.cut(marker)
    assembly=cq.Assembly(name=spec.get('name','reconstructed_package'))
    assembly.add(body,name='body_black',color=cq.Color(0,0,0))
    assembly.add(cq.Compound.makeCompound(contacts),name='metal_contacts',color=cq.Color(.72,.74,.76))
    if marker:assembly.add(marker,name='pin1_orientation_dot',color=cq.Color(.9,.9,.9))
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_name(output.stem+'.temporary.step')
    if not exportAssembly(assembly,str(temporary),mode='default'):raise ValueError('STEP export failed')
    imported=cq.importers.importStep(str(temporary)).val();box=imported.BoundingBox()
    expected=1+len(contacts)+(1 if marker else 0)
    if not imported.isValid() or len(imported.Solids())!=expected:raise ValueError('STEP reimport validity/count failed')
    if any(abs(a-b)>1e-4 for a,b in [(box.xlen,w),(box.ylen,h),(box.zmin,0),(box.zmax,height)]):raise ValueError('STEP reimport envelope failed')
    text=temporary.read_text(encoding='ascii')
    rgb=[tuple(map(float,v)) for v in re.findall(r'COLOUR_RGB\([^,]*,\s*([-+\d.Ee]+),\s*([-+\d.Ee]+),\s*([-+\d.Ee]+)\)',text)]
    if (0.,0.,0.) not in rgb and "DRAUGHTING_PRE_DEFINED_COLOUR('black')" not in text:raise ValueError('Black style lost')
    if not rgb or (marker and 'pin1_orientation_dot' not in text):raise ValueError('Assembly colors/marker lost')
    temporary.replace(output)
    report={'kind':kind,'model_status':spec.get('model_status','locally reconstructed simplified nominal model'),'source':spec.get('source'),'units':'mm','contacts':len(contacts),'contact_positions':positions,'reimport_valid':True,'solids':expected,'envelope_mm':[box.xlen,box.ylen,box.zmax],'all_contacts_seated_at_z0':True,'black_body_style_present':True,'marker':spec.get('marker'),'marker_factory_dimensions_verified':False,'GUI_alignment_verified':False}
    output.with_suffix('.validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('spec',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();print(json.dumps(build(json.loads(args.spec.read_text(encoding='utf-8-sig')),args.output)))
