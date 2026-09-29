"""Dependency-free behavioural test using a fake PyAlembic API."""
import tempfile
from types import SimpleNamespace
from exporters.alembic_exporter import AlembicExporter

class Schema:
    def __init__(self): self.samples=[]
    def set(self,sample): self.samples.append(sample)
class Obj:
    def __init__(self,*args): self.args=args; self.schema=Schema()
    def getSchema(self): return self.schema
class Archive:
    def __init__(self,path): self.path=path; self.top=object(); self.ts=[]
    def getTop(self): return self.top
    def addTimeSampling(self,value): self.ts.append(value); return 1
class Sample:
    def __init__(self): self.ops=[]; self.values={}
    def addOp(self,*value): self.ops.append(value)
    def __getattr__(self,name):
        if name.startswith('set'):
            return lambda value: self.values.__setitem__(name[3:],value)
        raise AttributeError(name)
class Op:
    def __init__(self,value): self.value=value
class Types:
    kTranslateOperation='T'; kRotateXOperation='RX'; kRotateYOperation='RY'; kRotateZOperation='RZ'
class V3d(tuple):
    def __new__(cls,*v): return tuple.__new__(cls,v)

created={}
def make_xform(*args): created['xform']=Obj(*args); return created['xform']
def make_camera(*args): created['camera']=Obj(*args); return created['camera']
Abc=SimpleNamespace(OArchive=Archive)
Core=SimpleNamespace(TimeSampling=lambda step,start:(step,start))
Geom=SimpleNamespace(OXform=make_xform,OCamera=make_camera,XformSample=Sample,CameraSample=Sample,XformOp=Op,XformOperationType=Types)

exporter=AlembicExporter(); exporter._imports=lambda:(Abc,Core,Geom,V3d)
keys=[SimpleNamespace(frame=1001,tx=1,ty=2,tz=3,rx=4,ry=5,rz=6,focal_length=35,focus_distance=200),SimpleNamespace(frame=1002,tx=2,ty=3,tz=4,rx=5,ry=6,rz=7,focal_length=36,focus_distance=210)]
track=SimpleNamespace(fps=25,keys=keys)
settings=SimpleNamespace(output_path=tempfile.mktemp(suffix='.abc'),archive_type='Ogawa',frame_step=1.0,rotation_order='XYZ')
exporter.export(track,settings)
assert len(created['xform'].schema.samples)==2
assert len(created['camera'].schema.samples)==2
assert created['xform'].schema.samples[0].ops[0][1]==(1,2,3)
assert created['camera'].schema.samples[1].values['FocalLength']==36
print('Alembic exporter behavioural test passed')
