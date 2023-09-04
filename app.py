from viktor import ViktorController
from viktor import File
from viktor.parametrization import ViktorParametrization, FileField, Text
from viktor.views import PDFView, PDFResult
from viktor.external.generic import GenericAnalysis
from pathlib import Path
from io import BytesIO


class Parametrization(ViktorParametrization):
    text = Text("""
## Revit X VIKTOR Proof-of-Concept

In this app you can upload a revit model.
The app then uses a generic worker to start and perform the data extraction in Revit.
The data in this case being the technical drawings of the FloorPlan views.
               
""")
                
    model = FileField('Upload your model')


class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization

    @PDFView("PDF Preview", duration_guess=10)
    def get_pdf_preview(self, params, **kwargs):
        floor_plans = self.run_pyrevit(params)
        print(type(floor_plans))

        return PDFResult(file=floor_plans)

    @staticmethod
    def run_pyrevit(params):
        command_path = Path(__file__).parent / "command.py"
        command = File.from_path(command_path).getvalue_binary()
        files=[('input.py', BytesIO(command)),
               ('model.rvt', BytesIO(params.model.file.getvalue_binary()))]

        generic_analysis = GenericAnalysis(files=files, executable_key="revit", output_filenames = ["output.pdf"])
        generic_analysis.execute(timeout=600)
        pdf_plans = generic_analysis.get_output_file("output.pdf", as_file=True)
        return pdf_plans

    # @staticmethod
    # def run_pyrevit():
    #     test_command = Path(__file__).parent / "test_command.py"
    #     command = File.from_path(test_command).getvalue_binary()
    #     files=[('input.py', BytesIO(command))]
    #     generic_analysis = GenericAnalysis(files=files, executable_key="revit", output_filenames = ["test.pdf"])
    #     generic_analysis.execute(timeout=600)
    #     pdf_plans = generic_analysis.get_output_file("test.pdf", as_file=True)
    #     return pdf_plans

