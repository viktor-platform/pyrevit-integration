import Autodesk
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInParameter, BuiltInCategory, Line, Wall, XYZ, Transaction
doc = __revit__.ActiveUIDocument.Document


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