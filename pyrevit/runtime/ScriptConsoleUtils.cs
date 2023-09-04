using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

#if (REVIT2013 || REVIT2014)
using Autodesk.Revit.UI.Selection;
#endif

namespace PyRevitLabs.PyRevit.Runtime {
    public class ScriptConsoleUtils {
        public static void ProcessUrl(UIApplication uiApp, string inputUrl) {
            var parsedQuery = HttpUtility.ParseQueryString(inputUrl.Split('?')[1]);

            if (parsedQuery["command"] == "select" && parsedQuery["element[]"] != null) {
                var idList = new List<ElementId>();
                foreach (string strId in parsedQuery["element[]"].Split(',')) {
#if !(REVIT2017 || REVIT2018 || REVIT2019 || REVIT2020 || REVIT2021 || REVIT2022 || REVIT2023)
                    idList.Add(new ElementId(Convert.ToInt64(strId)));
#else
                    idList.Add(new ElementId(Convert.ToInt32(strId)));
#endif
                }

                SelectElements(uiApp, idList, parsedQuery.AllKeys.Contains("show") && parsedQuery["show"] == "true");
            }
        }

        public static void SelectElements(UIApplication uiApp, List<ElementId> elementIds, bool show) {
            var uidoc = uiApp.ActiveUIDocument;

            if (uidoc != null) {
                var doc = uiApp.ActiveUIDocument.Document;

                // is there is only one element and it has owner view
                // open the view, isolate the element, zoom fit the view, unisolate
                // this would zoom in on that element only
                if (doc != null && elementIds.Count >= 1) {
                    // get all open ui views, to be able to zoom later on
                    var openUIViews = uidoc.GetOpenUIViews();

                    // get the first one
                    var el = doc.GetElement(elementIds[0]);

                    // if element is a view, open the view
                    Type elType = el.GetType();
                    if (elType == typeof(View) || elType.IsSubclassOf(typeof(View))) {
                        uidoc.ActiveView = (View)el;
                    }
                    // if element is a 2D element and has an owner view
                    // open the view and zoom to element
                    else if (el.OwnerViewId != ElementId.InvalidElementId) {
                        // if all 2D elements are in the same view
                        bool sameOwnerView = true;
                        foreach (var elid in elementIds)
                            if (doc.GetElement(elid).OwnerViewId != el.OwnerViewId)
                                sameOwnerView = false;

                        if (sameOwnerView) {
                            // get the view and activate
                            View view = (View)doc.GetElement(el.OwnerViewId);
                            uidoc.ActiveView = view;

                            // islolate the element, deselect, and zoom fit
                            // add host elements for tags since tags will not be visible without their host
                            var elementIdsToIsolate = new List<ElementId>();
                            foreach (var elid in elementIds) {
                                var element = doc.GetElement(elid);
#if !(REVIT2017 || REVIT2018 || REVIT2019 || REVIT2020 || REVIT2021 || REVIT2022)
                                if (element.GetType() == typeof(IndependentTag)) {
                                    var hostId = ((IndependentTag)element).GetTaggedLocalElementIds().FirstOrDefault();
                                    if (hostId != ElementId.InvalidElementId)
                                        elementIdsToIsolate.Add(hostId);
                                }
#else
                                    if (element.GetType() == typeof(IndependentTag)) {
                                    var hostId = ((IndependentTag)element).TaggedLocalElementId;
                                    if (hostId != ElementId.InvalidElementId)
                                        elementIdsToIsolate.Add(hostId);
                                }
#endif
                            }

                            elementIdsToIsolate.AddRange(elementIds);
                            // islolate the element, deselect, and zoom fit
                            if (show)
                                uidoc.ShowElements(elementIdsToIsolate);
                        }
                    }
                    // if element is a 3D element and does not have an owner view
                    // get the current view and try to zoom the element
                    else if (el.OwnerViewId == ElementId.InvalidElementId) {
                        // get the current view
                        View view = (View)uidoc.ActiveView;

                        // islolate the element, deselect, and zoom fit
                        if (show)
                            uidoc.ShowElements(elementIds);
                    }

                }

                // now select the element(s)

#if (REVIT2013 || REVIT2014)
                var elementSet = SelElementSet.Create();
                foreach (ElementId elId in elementIds) {
                    var element = doc.GetElement(elId);
                    if (element != null)
                        elementSet.Add(element);
                }

                uidoc.Selection.Elements = elementSet;
#else
                uidoc.Selection.SetElementIds(elementIds);
#endif

            }

        }
    }
}