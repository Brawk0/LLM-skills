"""Exercise meaningful mapping/orientation invariants using synthetic contacts."""
import argparse,json,tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
from build_symbol import build as symbol
from build_footprint import build as footprint

def run(with_step=False):
    with tempfile.TemporaryDirectory(prefix='component_skill_test_') as directory:
        out=Path(directory)
        s={'name':'SYNTHETIC_ADC','label_policy':{'append_ball':True},'pins':[{'ball':'1','name':'VINP1','type':'Input'},{'ball':'2','name':'D0P1','type':'Output','lvds':True,'dqs':'DQ0'},{'ball':'0','name':'AVSS_DVSS','type':'Power'}],
           'parts':[{'name':'SIGNALS','width':38.1,'height':15.24,'pins':[{'ball':'1','x':-19.05,'y':2.54,'side':'left'},{'ball':'2','x':19.05,'y':2.54,'side':'right'}],'texts':[{'text':'CHANNEL1','x':0,'y':5.08,'size':7}]},
                    {'name':'POWER','width':25.4,'height':10.16,'pins':[{'ball':'0','x':-12.7,'y':0,'side':'left'}]}]}
        report=symbol(s,out/'s.elixml');tree=ET.parse(out/'s.elixml').getroot()
        pins={p.findtext('PadNumber'):p for p in tree.findall('.//Pin')}
        assert len(pins)==3 and report['all_text_vector']
        assert tree.find('.//Part').get('RefDes')=='D'
        refdes_texts=tree.findall('.//Shape[@TextShow="RefDes"]')
        assert len(refdes_texts)==2 and all(t.findtext('TextLines/TextLine')=='D' for t in refdes_texts)
        assert pins['2'].findtext('Name')=='D0P1/LVDS/DQ0/2'
        assert pins['0'].get('ElectricType')=='Power'
        bad=dict(s);bad['parts']=[s['parts'][0]]
        try:symbol(bad,out/'bad.elixml')
        except ValueError:pass
        else:raise AssertionError('Missing EP was accepted')
        assert not (out/'bad.elixml').exists()
        b={'kind':'bga','name':'BGA_TEST','body':[5,5],'rows':['A','B','C'],'columns':3,'pitch':1,'pad_diameter':.5}
        br=footprint(b,out/'b.kicad_mod');bp={p['number']:p for p in br['pads']}
        assert len(bp)==9 and (bp['A1']['x'],bp['A1']['y'])==(-1,-1) and (bp['C3']['x'],bp['C3']['y'])==(1,1)
        q={'kind':'qfn','name':'QFN_TEST','body':[3,3],'pins_per_side':2,'pitch':.5,'land_length':.5,'land_width':.25,'land_center_offset':1.35,'ep':{'number':'0','width':1.2,'height':1.2},'paste_windows':[{'x':0,'y':0,'width':.8,'height':.8}]}
        qr=footprint(q,out/'q.kicad_mod');qp={p['number']:p for p in qr['pads']}
        assert len(qp)==9 and qp['1']['x']<0 and qp['1']['y']<0 and qp['3']['x']<0 and qp['3']['y']>0 and qp['5']['x']>0 and qp['5']['y']>0 and qp['7']['x']>0 and qp['7']['y']<0
        ep_line=next(l for l in (out/'q.kicad_mod').read_text().splitlines() if '(pad 0 ' in l)
        assert 'F.Paste' not in ep_line and '(fp_poly ' in (out/'q.kicad_mod').read_text()
        if with_step:
            from build_step import build as step
            bs=dict(b,height=1.0,standoff=.3,ball_diameter=.4,marker={'x':-1,'y':1,'diameter':.4,'depth':.02})
            sr=step(bs,out/'b.step');assert sr['solids']==11
            assert sr['contact_positions'][0]=={'number':'A1','x':-1.,'y':1.}
            qs={'kind':'qfn','body':[3,3],'height':1.0,'contact_height':.2,'contact_length':.4,'contact_width':.25,'contact_center_offset':1.3,'pins_per_side':2,'pitch':.5,'ep':{'width':1.2,'height':1.2,'thickness':.2},'marker':{'x':-1,'y':1,'diameter':.4,'depth':.02}}
            sr=step(qs,out/'q.step');assert sr['solids']==11
            assert sr['contact_positions'][0]['x']<0 and sr['contact_positions'][0]['y']>0
    print('PASS: complete contact map, vector text, alternate fields, BGA corners, QFN perimeter/EP/paste'+(', reimported colored BGA/QFN STEP' if with_step else ''))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--step',action='store_true');run(p.parse_args().step)
