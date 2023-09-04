import os 
import PyPDF2

# Command to run
command = 'pyrevit run "C:\\Users\\Thomas Nagels\\viktor-apps\\zz-worker\\script.py" "C:\\Users\\Thomas Nagels\\viktor-apps\\zz-worker\\model.rvt"'

if __name__ == '__main__':
    # Get the file path from the command line ( this file is passed with the command line)
    # Run the command
    os.system(command)

    x = [a for a in os.listdir() if a.endswith(".pdf")]

    merger = PyPDF2.PdfMerger()

    for pdf in x:
        merger.append(open(pdf, 'rb'))

    with open("output.pdf", "wb") as fout:
        merger.write(fout)