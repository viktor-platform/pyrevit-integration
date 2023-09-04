import os.path as op
from pyrevit import revit, HOST_APP
import Autodesk
import clr
import os
import time
from Autodesk.Revit.DB import *

clr.AddReference('revitAPI')
clr.AddReference('RevitAPIUI')

#somehow make this the model that gets uploaded, think of arguments to pass to worker
model = "C:\\Users\\Thomas Nagels\\viktor-apps\\zz-worker\\model.rvt"

uidoc = HOST_APP.uiapp.OpenAndActivateDocument(model)
doc = uidoc.Document



# Collect floor plan views
view_collector = FilteredElementCollector(doc).OfClass(Autodesk.Revit.DB.View)
floor_plans = [view for view in view_collector if view.ViewType == ViewType.FloorPlan]
print(floor_plans)
# Export each floor plan view as a PDF
pdf_options = PDFExportOptions()
for floor_plan in floor_plans:
    if floor_plan.CanBePrinted:
        filename = "FloorPlan_" + floor_plan.Name
        pdf_path = 'C:\\Users\\Thomas Nagels\\viktor-apps\\zz-worker'
        pdf_options = PDFExportOptions(FileName=filename)
        transaction = Transaction(doc, "Export PDF")
        transaction.Start()
        doc.Export(pdf_path, [floor_plan.Id], pdf_options)
        transaction.Commit()


print("waiting 10 secs for pdfs to load")
time.sleep(10)


# def merger():
#     x = [a for a in os.listdir() if a.endswith(".pdf")]

#     merger = PyPDF2.PdfMerger()

#     for pdf in x:
#         merger.append(open(pdf, 'rb'))

#     with open("test_full.pdf", "wb") as fout:
#         merger.write(fout)







