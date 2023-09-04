import sys 
import os.path as op


import Autodesk
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInParameter, BuiltInCategory, Line, Wall, XYZ, Transaction
#doc = __revit__.ActiveUIDocument.Document

from pyrevit import revit, HOST_APP



def return_wals_level(doc):
    """
    The above code defines two functions, "return_wals_level" and "get_lines", which are used to
    retrieve the level and wall type from a Revit document and create lines based on the level's
    elevation.
    
    :param doc: The "doc" parameter is expected to be a Revit document object. It is used to access the
    elements in the Revit project
    :return: The function `return_wals_level` returns the level object with an elevation of 0.0 and the
    wall type object with the name 'Wall-Subs_100Blk-75Con-100Blk'.
    """
    
    levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
    for level in levels:        
        elevation = level.get_Parameter(BuiltInParameter.LEVEL_ELEV).AsDouble()
        print(elevation)
        if elevation == 0.0:
            level_0 = level

    for wall in walls:
        name = wall.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        print(name)
        if name == 'Wall-Subs_100Blk-75Con-100Blk':
            wall_type = wall
    
    return level_0, wall_type

def get_lines(level_0):
    p_1 = XYZ(0,0,level_0.Elevation)
    p_2 = XYZ(50,0,level_0.Elevation)
    p_3 = XYZ(50,50,level_0.Elevation)
    line_1 = Line.CreateBound(p_1, p_2)
    line_2 = Line.CreateBound(p_2, p_3)
    lines = [line_1, line_2]

    return lines


def create_walls(doc):
    levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
    for level in levels:
        elevation = level.get_Parameter(BuiltInParameter.LEVEL_ELEV).AsDouble()
        print(elevation)
        if elevation == 0.0:
            level_0 = level

    for wall in walls:
        name = wall.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        print(name)
        if name == 'Wall-Subs_100Blk-75Con-100Blk':
            wall_type = wall
    p_1 = XYZ(0,0,level_0.Elevation)
    p_2 = XYZ(50,0,level_0.Elevation)
    p_3 = XYZ(50,50,level_0.Elevation)
    line_1 = Line.CreateBound(p_1, p_2)
    line_2 = Line.CreateBound(p_2, p_3)
    lines = [line_1, line_2]
    t = Transaction(doc, 'column')
    t.Start()
    for line in lines:
        wall_1 = Wall.Create(doc, line, wall_type.Id, level_0.Id, 3000/304.8, 0, False, True)
    t.Commit()



if __name__ == '__main__':
    print("test main")
    # Open here a text file 
    with open(op.join(op.dirname(__file__), 'models.txt'), 'w') as f:
        # Read the file and print the content
        f.write(repr(__models__))

    for model in __models__:
        
        uidoc = HOST_APP.uiapp.OpenAndActivateDocument(model)


        

        with revit.Transaction('Test transaction'):

            with open(op.join(op.dirname(__file__), 'type_doc.txt'), 'w') as f:
                # Read the file and print the content
                #f.write("type of storage:" + str(revit.doc.GetTypeOfStorage))
                f.write("Methods for revit object:" + str(dir(revit)))
                #f.write("Project information:" + str(revit.doc.ProjectInformation()))

                
            

            level, wall_type = return_wals_level(revit.doc)
            lines = get_lines(level)

            for line in lines:
                Wall.Create(revit.doc, line, wall_type.Id, level.Id, 3000/304.8, 0, False, True)
            revit.create.create_3d_view("test 3d view", doc = revit.doc)
        revit.doc.SaveAs("C:\\Users\\Luuk Boot\\viktor-apps\\test_revit_integration\\test1\\Project_test.rvt")
        revit.doc.Save()
        
        

        
                
                

            
       
       
       
        


            
        
        
        



    