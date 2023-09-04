# pyrevit-integration

Welcome to sample VIKTOR REVIT integration! 
This app shows you how a Revit integration can be made using a VIKTOR generic worker and pyRevit with Revit. The user provides the app with one of their models, with this model, the VIKTOR worker will use pyRevit and the command line to pass instructions to Revit. In this example the instructions are to render and export 2D floor plans of the model.
An example of how the app looks can be seen below.

![image](https://github.com/viktor-platform/pyrevit-integration/assets/123568967/adff379c-8358-43c7-9b84-5c44ea31ea2c)


## Preliminary downloads:
Some preliminary downloads that you will need apart from VIKTOR and Python:
- VIKTOR's [Generic Worker](https://docs.viktor.ai/docs/worker/)
-  Your preferred version of [Revit](https://www.autodesk.nl/products/revit/overview?term=1-YEAR&tab=subscription)
-  Download the [pyRevit version](https://github.com/eirannejad/pyRevit) corresponding to the version of Revit
-  Note: the method used to connect to Revit via Python also requires python on the machine that is running Revit. 

To get familiar with the tools that are needed you can consult docs of:
- pyRevit and pyRevit CLI [here](https://pyrevitlabs.notion.site/pyRevit-CLI-c50de95259114db795db5bd3f19f8e2a)
- The pyRevit [YouTube channel](https://www.youtube.com/c/pyRevit)
- Autodesk's [Revit API](https://www.revitapidocs.com/) and filter for your Revit version

## Getting started:

After cloning the repo, you will need to install the application as you normally would. Make sure to check/update the filepaths in each step!

Next it is important to make a working directory on the machine for the worker, this is where the worker will access inputs/outputs.

You must then take the steps to install and connect the worker to the correct workspace and make sure it will use the folder you just made as it's working directory.
- For this worker, it is important to connect to python. Python will use the command line to run pyRevit and thus be able to work with Revit. 
- In this example, the script is added to the worker to prevent cluttering of the app. If you do not have access to the worker to upload your script, then you can add it as an input to for the worker. Make sure to update the config if you decide to do so! (Note: the file path will not change because the file will be  

An example of the code for the file named config.yaml is shown below:

```
executables:
  revit:
    path: 'C:\PATH\TO\PYTHON\Python\Python311\python.exe'
    arguments:
    - 'input.py'
    - 'model.rvt'
    workingDirectoryPath: 'C:\PATH\TO\WORKING\DIRECTORY\worker'
maxParallelProcesses: 1 # must be one, please do not change
```


If you have the worker on your machine, check that your worker is correctly connected, you can do this by running it as an Administrator, you will need these rights activated on the machine that is hosting the worker and Revit. (if you have the desktop shortcut installed you can right-click the shortcut and it shoud tell you that the connection is succesfull.)
You will also be able to see if your worker is online by navigating to VIKTOR in your browser, e.g. cloud.viktor.ai, and in the tab workers, it should indicate that there is a worker available. 

In the working directory that you have for the worker, add a file called 'script.py' or something that will indicate that this is the set of instructions for Revit. If you decide to add the script.py as an input for the worker you can skip this step.
- In this example you will find that script.py is the set of instructions that filters the 2D Floor plans from all the other views, renders and then exports them.
- 
Next it is recommended to add a command.py file to your VIKTOR app. This will become one of the inputs for the generic worker and it contains the command that the worker will use in the Command-Line Interface to work in Revit.
- If you are interested in the source of this method to use pyRevit via the CLI, check out this [video](https://www.youtube.com/watch?v=_HldsaHA8i8) where the founder of pyRevit explains it in more detail.
- Also explained in this video is how to use different versions of Revit through the pyrevit CLI.

To start using the worker, import the tools into your 'app.py' that you will need to perform the generic analysis, make sure that this is the same as the arguments in your config file. 

## Further Improvements
As you will notice, this app is quite slow. Almost all of time is going into starting Revit. Therefore I would like to invite all developers interested to let me know if you find a solution that can use an instance of Revit that is already open.
I have already found that running the app headless is a great way to shave off some running time however the app does still needto render quite some Views in the background for the export. 

