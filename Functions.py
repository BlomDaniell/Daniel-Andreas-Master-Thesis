#Daniel Blom & Andreas Hedlunds functions code

#Path to Functions
"execfile('G:\Master thesis\Abaqus Programing tutorial\BeamWithParameters\CompletCode\Functions')"


    #Imports Modules to use in Abaqus
from abaqus import *
from abaqusConstants import *
from caeModules import*
import numpy as np
from odbAccess import*


    #Creats node set
def Create_Node_Set_ByBoundingBox(model,part,x1,y1,z1,x2,y2,z2,set_name):
    p = mdb.models[model].parts[part]
    n = p.nodes
    nodes = n.getByBoundingBox(x1,y1,z1,x2,y2,z2)
    p.Set(nodes=nodes, name=set_name)
    
    #Creats element
def Create_Element_Set_ByBoundingBox(model,part,x1,y1,z1,x2,y2,z2,Element_name):
    p = mdb.models[model].parts[part]
    e = p.elements
    elements = e.getByBoundingBox(x1,y1,z1,x2,y2,z2)
    p.Set(elements=elements, name=Element_name)

    #Creates Geometric
def Create_Surface_Set_Coordiantes(Model,Part_Name,Set_Name,Coordinates,Number_of_Surfaces):
    p = mdb.models[Model].parts[Part_Name]
    f = p.faces
    facesT = f.findAt() # since it needs to be assigned before used
    for i in range(0,Number_of_Surfaces):
        ii= int(i)
        faces = f.findAt(((Coordinates[0+(ii*3)],Coordinates[1+(ii*3)],Coordinates[2+(ii*3)]), ),)
        if not facesT:
            facesT = faces
        else:
            facesT += faces
    p.Set(faces=facesT, name=Set_Name)

    #Creats Mesh
def Create_Mesh_part(Model,Part_Name,MeshSize):
    p = mdb.models[Model].parts[Part_Name]
    p.seedPart(size=MeshSize, deviationFactor=0.1, minSizeFactor=0.1)
    p = mdb.models[Model].parts[Part_Name]
    p.generateMesh()
    #Creats Material
def Create_Material(Model,Material_Name,Density,Elastic,Plastic):
    mdb.models[Model].Material(name=Material_Name)
    mdb.models[Model].materials[Material_Name].Density(table=(Density))
    mdb.models[Model].materials[Material_Name].Elastic(table=((Elastic), ))
    mdb.models[Model].materials[Material_Name].Plastic(table=(Plastic))

    #Creats section
def Create_Section(Model,Section_Name,Material,Thickness):
    mdb.models[Model].HomogeneousShellSection(name=Section_Name, 
    preIntegrate=OFF, material=Material, thicknessType=UNIFORM, 
    thickness=Thickness, thicknessField='', nodalThicknessField='', 
    idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT, 
    thicknessModulus=None, temperature=GRADIENT, useDensity=OFF, 
    integrationRule=SIMPSON, numIntPts=5)

    #Assigns section
def Assign_Section(Model,Part_Name,Section_Name,Offset,Offsettype,Set):
    p = mdb.models[Model].parts[Part_Name]
    region = p.sets[Set]
    p = mdb.models[Model].parts[Part_Name]
    p.SectionAssignment(region=region, sectionName=Section_Name, offset=Offset, 
        offsetType=Offsettype, offsetField='', 
        thicknessAssignment=FROM_SECTION)
#   MIDDLE_SURFACE TOP_SURFACE

    #Adds part to assembly
def Add_Part_To_Assembly(Model,Part_Name,Instance_Name):
    a = mdb.models[Model].rootAssembly
    p = mdb.models[Model].parts[Part_Name]
    a.Instance(name=Instance_Name, part=p, dependent=ON)

    #Create Dynamci Step
def Create_Step(Model,Step_Name,Previous_Step,Description,Time_Period,Target_Time_Increment):
    mdb.models[Model].ExplicitDynamicsStep(name=Step_Name, 
    previous=Previous_Step, description=Description, timePeriod=Time_Period, 
    massScaling=((SEMI_AUTOMATIC, MODEL, AT_BEGINNING, 0.0, Target_Time_Increment, 
    BELOW_MIN, 0, 0, 0.0, 0.0, 0, None), ), improvedDtMethod=ON)
 
    #Interaction
def Create_Friction(Model,Step_Name,Contact_Property,Interaction_Properties,Interaction_Name,Friction_Coeff):     
    mdb.models[Model].ContactProperty(Contact_Property)
    mdb.models[Model].interactionProperties[Interaction_Properties].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, 
        table=((Friction_Coeff, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION, 
        fraction=0.005, elasticSlipStiffness=None)
    mdb.models[Model].ContactExp(name=Interaction_Name, 
        createStepName=Step_Name)
    mdb.models[Model].interactions[Interaction_Name].includedPairs.setValuesInStep(
        stepName=Step_Name, useAllstar=ON)
    mdb.models[Model].interactions[Interaction_Name].contactPropertyAssignments.appendInStep(
        stepName=Step_Name, assignments=((GLOBAL, SELF, Interaction_Properties), ))
    
    #Fix a node set
def Fix_Nodes(Model,Step_Name,BC_Name,Instance_Name,Node_Set):
    a = mdb.models[Model].rootAssembly
    region = a.instances[Instance_Name].sets[Node_Set]
    mdb.models[Model].EncastreBC(name=BC_Name, 
        createStepName=Step_Name, region=region, localCsys=None)

    #Creates a new history output
def Creat_History_Output(Model,Set,Step,Request_Parameter,Time_Interval,Request_Name):
    regionDef=mdb.models[Model].rootAssembly.sets[Set]
    mdb.models[Model].HistoryOutputRequest(name=Request_Name, 
        createStepName=Step, variables=(Request_Parameter, ), timeInterval=Time_Interval, 
        region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)


    #Creates U history output
    a = mdb.models['CrashSimulationModel1'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Dynamic')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        adaptiveMeshConstraints=ON, optimizationTasks=OFF, 
        geometricRestrictions=OFF, stopConditions=OFF)
    regionDef=mdb.models[Model].rootAssembly.allInstances['Wall_Instance'].sets['Wall_Set']
    mdb.models[Model].HistoryOutputRequest(name='U', 
        createStepName=Step, variables=('U3', ), timeInterval=Time_Interval, 
        region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    

    #Creates Stop criteria history output
    mdb.models[Model].OperatorFilter(name='Stop-Criteria', operation=MIN, 
        limit=0, halt=ON)
    regionDef=mdb.models[Model].rootAssembly.sets['Wall_Instance.Wall_Set']
    mdb.models[Model].HistoryOutputRequest(name='Stop-Criteria-Velocity', 
        createStepName=Step, variables=('V3', ), timeInterval=Time_Interval, 
        region=regionDef, filter='Stop-Criteria', sectionPoints=DEFAULT, 
        rebar=EXCLUDE)
    

    mdb.models[Model].FieldOutputRequest(name='F-Output-1', 
        createStepName=Step, variables=('A','CSTRESS','EVF','LE','PE','PEEQ','PEEQVAVG','PEVAVG','RF','S','SVAVG','U','V','EVOL', ), timeInterval=Time_Interval)

    #Creats a new field output
def Creat_Field_Output(Model,Instance,Set,Step,Request_Parameter,Time_Interval,Request_Name):
    regionDef=mdb.models[Model].rootAssembly.allInstances[Instance].sets[Set]
    mdb.models[Model].FieldOutputRequest(name=Request_Name, 
        createStepName=Step, variables=(Request_Parameter, ), timeInterval=Time_Interval, 
        region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)

    #Creates new job and start simulation
def Create_Simulation(Model,Simulation_Name,Description,numDomains,numCpus):
    mdb.Job(name=Simulation_Name, model=Model, description=Description, 
    type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
    memory=90, memoryUnits=PERCENTAGE, explicitPrecision=SINGLE, 
    nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, 
    contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', 
    resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=1, 
    activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1)
    mdb.jobs[Simulation_Name].submit(consistencyChecking=OFF)
    mdb.jobs[Simulation_Name].waitForCompletion()

    #Creates beams form txt file coordinates
def Create_part_from_txt(Model,Sketch_Name,Datafile_Name,Length,Line_Nr):
    linecounter=0 # count which line we are on
    file=open(Datafile_Name,"r") #Opens the text file
    for line in file:
     
        Splitline=line.split(",") #splits up the line when it sees a ","
        if linecounter==0:    
            Numbers_of_rows=int(Splitline[0]) #Stores the numbers of rows the file not including the first line
            Most_numbers_of_element=int(Splitline[1]) #Stores the numbers of elements in the 
        elif linecounter==1:
            Number_of_elements=len(Splitline)
            array = [ [0]*Most_numbers_of_element for i in range(Numbers_of_rows)] # Creates the array
    
            for i in range(0,Number_of_elements):
                array[(linecounter-1)][i]=int(Splitline[i]) 
        else:
            Number_of_elements=len(Splitline)
            for i in range(0,Number_of_elements):
                array[(linecounter-1)][i]=int(Splitline[i])

        linecounter=linecounter+1

    temp=0
    #Lines
    ArrayMulti=[1,2,3,4]
    for temp in range(0,((array[Line_Nr-1][temp]))):
        strnumber=str(Line_Nr)
        if temp ==0:
            s = mdb.models[Model].ConstrainedSketch(name='Profile'+strnumber, sheetSize=200.0)
            g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints

        s.Line(point1=(array[Line_Nr-1][temp+ArrayMulti[0]], array[Line_Nr-1][temp+ArrayMulti[1]]),
                point2=(array[Line_Nr-1][(temp+ArrayMulti[2])], array[Line_Nr-1][(temp+ArrayMulti[3])]))
        ArrayMulti[0]=ArrayMulti[0]+3
        ArrayMulti[1]=ArrayMulti[1]+3
        ArrayMulti[2]=ArrayMulti[2]+3
        ArrayMulti[3]=ArrayMulti[3]+3
        

    #Creats the part  form the sketch
    p = mdb.models[Model].Part(name=Sketch_Name+strnumber, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    #Creats the extrusion
    p.BaseShellExtrude(sketch=s, depth=Length)
    del mdb.models[Model].sketches['Profile'+strnumber]

def Creates_The_Results(Step,WallRF,Job_Name,Part_Name,Set_Name,instance_Set,strnumber,volumeList,MassList,xx,Result_Location):
    JobName=Job_Name+".odb"
    PartName=Part_Name.upper() ###'BEAM1_INSTANCE'
    SetInPart=Set_Name.upper()##Set_Name 'FIXED_NODES1'
    SetNameHistory=Set_Name.upper()
    WallRF="REFERENCE_POINT_"+WallRF+"        1"
    ii=strnumber
    

    odb1=session.openOdb('G:\MASTER_THESIS\DanielKOD\CompletCode\Crash'+ii+'.odb')
    NODES=odb1.rootAssembly.instances[PartName].nodeSets[SetInPart].nodes
    NODE_LABELS=[]

    for i in range(len(NODES)):
     
        NODE_LABELS.append(odb1.rootAssembly.instances[PartName].nodeSets[SetInPart].nodes[i].label)

    NODE_LABELS_str=[]



    NODE_LABELS_str = map(str,NODE_LABELS)

    XyPlotList=[0]*(len(NODES))

    Txt1='Reaction force: RF3 PI: '+PartName+' Node '
    Txt2=' in NSET '+SetNameHistory
    TxtList=[]


    for i in range(len(NODES)):
        x = NODE_LABELS_str[i]
        y = Txt1+x+Txt2
        TxtList.append(y)



    for i in range(len(NODES)):

        XyPlotList[i] = xyPlot.XYDataFromHistory(odb=odb1, 
        outputVariableName=TxtList[i], 
        steps=(Step, ), suppressQuery=True, __linkedVpName__='Viewport: 1')


    Txt3 = 'XyPlotList['
    Txt4 = '],'

    XyList=[]

    for i in range(len(NODES)):
        x1 = str(i)
        y1 = Txt3+x1+Txt4
        XyList.append(y1)

    XyListString = ' '.join([str(item) for item in XyList])

    for i in range(len(NODES)):
        x = NODE_LABELS_str[i]
        y = Txt1+x+Txt2
        TxtList.append(y)




    for i in range(len(NODES)):
        
        XySum = sum((eval(XyListString,None,None) , ), )

    session.XYData(name='RF3'+ii, objectToCopy=XySum, 
            sourceDescription='sum((RF3'+ii+', ),)')

    xy1 = session.xyDataObjects['RF3'+ii]
    xyMag = vectorMagnitude(xy1)
    xyMag.setValues(sourceDescription='vectorMagnitude ( "RF3"'+ii+' )')
    tmpName = xyMag.name
    session.xyDataObjects.changeKey(tmpName, 'RF3-Mag'+ii)
    session.linkedViewportCommands.setValues(_highlightLinkedViewports=False)


    xy_result = session.XYDataFromHistory(name='U3'+ii, odb=odb1, 
        outputVariableName='Spatial displacement: U3 PI: WALL_INSTANCE Node 1 in NSET WALL_SET', 
        steps=(Step, ), __linkedVpName__='Viewport: 1')

    xy1 = session.xyDataObjects['RF3-Mag'+ii]
    xy2 = session.xyDataObjects['U3'+ii]
    xy3 = combine(xy1, xy2)
    xyp = session.XYPlot('XYPlot-'+ii)
    chartName = xyp.charts.keys()[0]
    chart = xyp.charts[chartName]
    c1 = session.Curve(xyData=xy3)
    chart.setValues(curvesToPlot=(c1, ), )
    session.viewports['Viewport: 1'].setValues(displayedObject=xyp)
    xy1 = session.xyDataObjects['U3'+ii]
    xy2 = session.xyDataObjects['RF3-Mag'+ii]
    xy3 = combine(xy1, xy2)
    xy3.setValues(sourceDescription='combine ( "U3"'+ii+', "RF3-Mag" )')
    tmpName = xy3.name
    session.xyDataObjects.changeKey(tmpName, 'RF3Diff'+ii)

    Excel1 = session.xyDataObjects['RF3-Mag'+ii]


    xy1 = session.xyDataObjects['RF3Diff'+ii]
    xy3 = integrate(xy1)/1000
    xy3.setValues(sourceDescription='integrate ( "RF3Diff" )')
    tmpName = xy3.name
    session.xyDataObjects.changeKey(tmpName, 'TotalE'+ii)
    xy1 = session.xyDataObjects['RF3Diff'+ii]
    xy3 = integrate(xy1)/1000
    xyp = session.xyPlots['XYPlot-'+ii]
    chartName = xyp.charts.keys()[0]
    chart = xyp.charts[chartName]
    c1 = session.Curve(xyData=xy3)
    chart.setValues(curvesToPlot=(c1, ), )


    lastFrame = odb1.steps['Dynamic'].frames[0]
    volumeField = lastFrame.fieldOutputs['EVOL']
    nucleus = odb1.rootAssembly.instances[PartName].elementSets['SECTION_SETBEAM'+ii]
    volumeSet = volumeField.getSubset(region=nucleus, elementType='S4R')
    volumeFieldValues = volumeSet.values

 
    volume = 0

    for vol in volumeFieldValues:
       volume += vol.data
       
    volumeList.append(volume)
    
#--- Exports the results to Excel---
#--- Gets SEA value ready for export---
    m = (volumeList[ii-1])*0.0000027*1000
    MassList.append(m)

    Temp1 = session.xyDataObjects['TotalE'+strnumber]
    Temp2 = MassList[ii-1]
    Excel2 = Temp1/Temp2

    size=len(Excel2)
    tempo=[0]*(size)

    for i in range(0,size):
        trans=str(Excel2[i])
        trans=trans.split(",")
        trans=trans[1].split(")")
        tempo[i]=trans[0]

    store=np.float_(tempo[:])

#--- Gets Diff3 value ready for export---
    size2=len(Excel1)
    tempo2=[0]*(size2)


    for i in range(0,size2):
        trans2=str(Excel1[i])
        trans2=trans2.split(",")
        trans2=trans2[1].split(")")
        tempo2[i]=trans2[0]

    store2=np.float_(tempo2[:])

    np.savetxt(Result_Location + "RF3Diff" +ii+ '.csv',store2,delimiter='.',fmt='%d')
    np.savetxt(Result_Location + "SEA" +ii+ '.csv',store,delimiter='.',fmt='%f')
