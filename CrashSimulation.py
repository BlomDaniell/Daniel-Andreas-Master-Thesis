#Daniel Blom & Andreas Hedlunds code for createing Crash simulation

#Path to CrashSimulation
"execfile('G:\MASTER_THESIS\DanielKOD\CompletCode\CrashSimulation.py')"


#Imports Modules to use in Abaqus
from abaqus import *
from abaqusConstants import *
from caeModules import*
import __main__
import xyPlot

#Changes the work directory
os.chdir(r"G:\MASTER_THESIS\DanielKOD\CompletCode")

#Import functions  
from Functions import*
from BuildWallFunction import*


#---Parameters-----
Model   = "CrashSimulationModel"
Part    = "Beam"
Step1   = "Initial" # This parameter is predefined by Abaqus and should not be changed.
Step2   = "Dynamic"
Beam_Length      = float(100)
Thickness   = float(2)
BeamSection = "BeamSection"
Material    = "A6060 T5"
Database    = "Database.txt"
MassScalingFactor   = float(5e-7)
WallMass            = float(0.1)
WallVelocity        = float(8000)
FrictionCoefficient = float(0.45)
MeshSize    = float(2)
Time_Period = float(0.1)
Wall_Height = float(250)
Wall_Length = float(300)
Wall_To_Beam_Distance   = 0.0
History_Time_Interval  = 0.00005
Section_Offset  = 0.0
Result_Location = "G:\\MASTER_THESIS\\DanielKOD\\CompletCode\\Results\\"
NumbersDomains  = 4
NumbersCpus = 4

#---Arrays-----
volumeList  = []
MassList    = []

#---Material Parameters-----
Density     =   (2.7e-09,),
Elastic     =   695000.0, 0.33
Plastic     =   (218.8, 0.0), (219.824,	0.007769), (221.247, 0.009316), (223.046, 0.011314),(224.304, 0.013601),(225.509,0.016112),(227.546,0.019396),(229.489,	0.023559),(231.403,	0.027379),(233.142,	0.030849),(235.751,	0.035683),(237.318,	0.0404),(239.755,0.04656),(241.845,	0.052642),(244,	0.060513),(245.264,	0.073787),(245.399,	0.081466),(245.405, 0.087099)


#---Imports basic informaion from txt file---
file=open(Database,"r")
line=file.readline()
Splitline=line.split(",")
Numbers_of_rows=int(Splitline[0])

#---Starts the loop for the hole program---
for i in range(1,(Numbers_of_rows+1)): 
    
    #---Creates the new Model---
    strnumber=str(i)
    InternModel=Model+strnumber
    mdb.Model(name=InternModel, modelType=STANDARD_EXPLICIT)
    
    #---If Model-1 exist it delets it sicne it is predefined to be created when the program restarts---
    if 'Model-1' in mdb.models: del mdb.models['Model-1']

    #---Calls for all the functions ---
    Create_Material(InternModel,Material,Density,Elastic,Plastic)

    Create_Step(InternModel,Step2,Step1,"This is the dynamic for the simulation",Time_Period,MassScalingFactor)

    Create_Section(InternModel,BeamSection,Material,Thickness)

    Build_Wall(InternModel,"Wall",Wall_Height,Wall_Length,"Wall_Instance",Wall_To_Beam_Distance,"Mass_Ineria_Wall",
                   WallMass,"Wall_Set","Wall_Surface","Fixed_wall",Step1,WallVelocity)

    Create_part_from_txt(InternModel,Part,Database,Beam_Length,i)

    Create_Friction(InternModel,Step2,"Friction","Friction","Contact_all",FrictionCoefficient)
    
    Create_Mesh_part(InternModel,Part+strnumber,MeshSize)
    
    Create_Node_Set_ByBoundingBox(InternModel,Part+strnumber,-100,-100,Beam_Length-1,100,100,Beam_Length,"Fixed_Nodes"+strnumber)
    
    Add_Part_To_Assembly(InternModel,Part+strnumber,Part+strnumber+"_Instance")

    Fix_Nodes(InternModel,"Initial","Fixed_Nodes",Part+strnumber+"_Instance","Fixed_Nodes"+strnumber)
    
    Create_Element_Set_ByBoundingBox(InternModel,Part+strnumber,-200,-200,-20,200,200,Beam_Length+100,"Section_Set"+Part+strnumber)
    
    Assign_Section(InternModel,Part+strnumber,Part+"Section",Section_Offset,MIDDLE_SURFACE,"Section_Set"+Part+strnumber)
    
    Creat_History_Output(InternModel,Part+strnumber+"_Instance.Fixed_Nodes"+strnumber,Step2,'RF3',History_Time_Interval,"RF")
    del mdb.models[Model+strnumber].historyOutputRequests['H-Output-1']
    
    Create_Simulation(InternModel,"Crash"+strnumber,NumbersDomains,NumbersCpus)

    Creates_The_Results(Step2,"WALL_INSTANCE","Crash"+strnumber,Part+strnumber+"_INSTANCE",
    "Fixed_Nodes"+strnumber,Part+strnumber+"_INSTANCE.Fixed_Nodes"+strnumber,strnumber,volumeList,MassList,i,Result_Location)


    xy1 = session.xyDataObjects['TotalE'+strnumber]
    xy2 = MassList[0]
    xy3 = xy1/xy2
    xyp = session.xyPlots['XYPlot-'+strnumber]
    chartName = xyp.charts.keys()[0]
    chart = xyp.charts[chartName]
    c1 = session.Curve(xyData=xy3)
    chart.setValues(curvesToPlot=(c1, ), )
    tmpName = xy3.name
    session.xyDataObjects.changeKey(tmpName, 'SEA'+strnumber)




 

        
