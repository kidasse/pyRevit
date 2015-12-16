import sys
from Autodesk.Revit.DB import *
from System.Collections.Generic import List
from Autodesk.Revit.UI import TaskDialog

uidoc = __revit__.ActiveUIDocument
activeDoc = __revit__.ActiveUIDocument.Document

class CopyUseDestination( IDuplicateTypeNamesHandler ):
	def OnDuplicateTypeNamesFound( self, args):
		return DuplicateTypeAction.UseDestinationTypes

def error(msg):
	TaskDialog.Show('RevitPythonShell', msg)
	sys.exit(0)

#find open documents other than the active doc
openDocs = [d for d in __revit__.Application.Documents if not d.IsLinked]
openDocs.remove( activeDoc )
if len( openDocs ) < 1:
	error('Only one active document is found. At least two documents must be open. Operation cancelled.')

#get a list of selected legends
selection = [ activeDoc.GetElement( elId ) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds() if activeDoc.GetElement( elId ).ViewType == ViewType.Legend ]

if len(selection) > 0:
	for doc in openDocs:
		print('\n---PROCESSING DOCUMENT {0}---'.format( doc.Title ))
		#get the first style for Drafting views. This will act as the default style
		cl = FilteredElementCollector( doc ).OfClass( ViewFamilyType )
		for type in cl:
			if type.ViewFamily == ViewFamily.Drafting:
				draftingViewType = type
				break
		#iterate over source legend views
		for srcView in selection:
			print('\nCOPYING {0}'.format( srcView.ViewName ))
			#get legend view elements and exclude non-copyable elements
			viewElements = FilteredElementCollector(activeDoc, srcView.Id).ToElements()
			elementList = []
			for el in viewElements:
				if isinstance( el, Element ) and el.Category and el.Category.Name != 'Legend Components':
					elementList.append( el.Id )
				else:
					print('SKIPPING ELEMENT WITH ID: {0}'.format( el.Id ))
			if len(elementList) < 1:
				print('SKIPPING {0}. NO ELEMENTS FOUND.'.format( srcView.ViewName ))
				continue
			#start creating views and copying elements
			with Transaction( doc, 'Duplicate Legend as Drafting') as t:
				t.Start()
				destView = ViewDrafting.Create( doc, draftingViewType.Id )
				options = CopyPasteOptions()
				options.SetDuplicateTypeNamesHandler( CopyUseDestination())
				copiedElement = ElementTransformUtils.CopyElements(	srcView,
																	List[ElementId]( elementList ),
																	destView,
																	None,
																	options )
				#matching element graphics overrides and view properties
				for dest, src in zip(copiedElement, elementList):
					destView.SetElementOverrides( dest, srcView.GetElementOverrides( src ))
				destView.ViewName = srcView.ViewName
				destView.Scale = srcView.Scale
				t.Commit()
else:
	error('At least one Legend view must be selected.')