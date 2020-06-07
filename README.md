# RiggingToolkit
Evolving toolset used to speed up my rigging workflow


To Install:

1) in maya/year/scripts add a userSetup.py
 add:
```python
import sys
sys.path.append('PATH TO THE PYTHON FOLDER INSIDE RIGGING TOOLKIT DEV eg C:\RiggingToolkitDEV\Python')
```

2) inside maya, anywhere you would execute python
```python
import acid_RiggingKit as ark
ark.CreateLegFromLocatorsUI().GenerateUI()
```

Currently I have only completed the creation of an IK setup for a Leg.
feed it locator names via the buttons ot typing it in, to set up a simple leg

<div style="width:100%;height:0px;position:relative;padding-bottom:48.696%;"><iframe src="https://streamable.com/e/3s7dgz" frameborder="0" width="100%" height="100%" allowfullscreen style="width:100%;height:100%;position:absolute;left:0px;top:0px;overflow:hidden;"></iframe></div>
