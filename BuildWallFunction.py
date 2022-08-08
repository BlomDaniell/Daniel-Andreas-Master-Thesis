#Daniel Blom & Andreas Hedlunds Build analytic wall code

#Path to Build_Wall_Function
"execfile('G:\Master thesis\Abaqus Programing tutorial\BeamWithParameters\CompletCode\BuildWallFunction')"

#Imports Modules to use in Abaqus
from abaqus import *
from abaqusConstants import *
from caeModules import*

#Imports functions
from Functions import*

def Build_Wall(Model,Part_Name,Wall_Height,Wall_length,Instance_Name,Distance_To_Beam,Inertia_Name,
               Inertia_Mass,Set_Name,Surface_Name,Displacement_Name,Step_name,Velocity):
    
    #Creats the rigid_Wall
    s = mdb.models[Model].ConstrainedSketch(name='__profile__', sheetSize=200)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.Line(point1=(Distance_To_Beam, -(Wall_Height/2)), point2=(0, (Wall_Height/2)))
    s.VerticalConstraint(entity=g[2], addUndoState=False)
    s.ObliqueDimension(vertex1=v[0], vertex2=v[1], textPoint=(18.2440872192383, 0.755908966064453), value=Wall_Height)
    p = mdb.models[Model].Part(name=Part_Name, dimensionality=THREE_D, type=ANALYTIC_RIGID_SURFACE)
    p = mdb.models[Model].parts[Part_Name]
    p.AnalyticRigidSurfExtrude(sketch=s, depth=Wall_length)
    s.unsetPrimaryObject()
    p = mdb.models[Model].parts[Part_Name]
    del mdb.models[Model].sketches['__profile__']

    Add_Part_To_Assembly(Model,Part_Name,Instance_Name)

    #rotate Wall
    a = mdb.models[Model].rootAssembly
    a.rotate(instanceList=(Instance_Name, ), axisPoint=(0.0, 0.0, 0.0), 
        axisDirection=(0.0, Wall_Height, 0.0), angle=90.0)

    #Creates REf point on rigid wall
    p = mdb.models[Model].parts[Part_Name]
    v2, e1, d2, n1 = p.vertices, p.edges, p.datums, p.nodes
    p.ReferencePoint(point=v2[3])

    #Creats a Mass_inertia on the ref point created above
    p = mdb.models[Model].parts[Part_Name]
    r = p.referencePoints
    refPoints=(r[2], )
    region=p.Set(referencePoints=refPoints, name=Set_Name)
    mdb.models[Model].parts[Part_Name].engineeringFeatures.PointMassInertia(
    name=Inertia_Name, region=region, mass=Inertia_Mass, alpha=0.0, composite=0.0)

    #Creats Set of RefpointWall
    p = mdb.models[Model].parts[Part_Name]
    r = p.referencePoints
    refPoints=(r[2], )
    p.Set(referencePoints=refPoints, name=Set_Name)

    #Creats surface on the wall
    a = mdb.models[Model].rootAssembly
    s1 = a.instances[Instance_Name].faces
    side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
    a.Surface(side1Faces=side1Faces1, name=Surface_Name)

    #Fix Wall By RF Point
    a = mdb.models[Model].rootAssembly
    region = a.instances[Instance_Name].sets[Set_Name]
    mdb.models[Model].DisplacementBC(name=Displacement_Name, 
        createStepName=Step_name, region=region, u1=0.0, u2=0.0, u3=UNSET, 
        ur1=0.0, ur2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)

    #Adding velocity to the wall
    a = mdb.models[Model].rootAssembly
    region = a.instances[Instance_Name].sets[Set_Name]
    mdb.models[Model].Velocity(name='Wall_Velocity', region=region, 
        field='', distributionType=MAGNITUDE, velocity3=Velocity, omega=0.0)