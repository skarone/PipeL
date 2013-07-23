import maya.OpenMayaUI as mui
import sip


def GetMayaLayout(layoutString):
    '''
    Will return the correct QT object for a given UI string.

    :param layoutString: `str`
    :returns: `QWidget`

    >>> GetMayaLayout('MayaWindow|MainAttributeEditorLayout')
    '''
    ptr = mui.MQtUtil.findLayout(layoutString)
    if ptr:
        return sip.wrapinstance(long(ptr), QtCore.QObject)

def GetWindow(windowName):
    '''
    Will get a child floating QWidget of the Maya Main Window
    :param windowName: `str` eg "AssetBrowserForm"

    :returns: `QWidget`
    '''
    ptr = mui.MQtUtil.findWindow(windowName)
    if ptr:
        return sip.wrapinstance(long(ptr), QtCore.QObject)

def GetFullName(QObject):
    '''
    Get the fullName of a QObject
    '''
    pointer = sip.unwrapinstance(QObject)
    if type(pointer) == long:
        windowString = mui.MQtUtil.fullName(pointer)
        if windowString:
            return windowString
        else:
            return ""
    else:
        # Fix for bug in 32bit Maya.... build the long name as we search for the QObject
        return GetQtWidget(QObject.objectName(), LongName = True)[-1]


def GetMayaMainWindow():
    '''
    :returns: `QtWidget` that pertains to the Maya Main Window
    '''

    ptr = mui.MQtUtil.mainWindow()
    if ptr:
        return sip.wrapinstance(long(ptr), QtCore.QObject)


def GetQtWidget(QWidgetName, LongName=False):
    '''
    :param QWidgetName: `str`
    :returns: `QtWidget` that pertains to the maya interface
    '''
    RootName = str(GetMayaMainWindow().objectName())
    Name = QWidgetName.split("|")[-1]
    for w in QtGui.qApp.topLevelWidgets():
        try:
            if w.objectName() == Name:
                if LongName:
                    return (w, "|" + "|".join([RootName, QWidgetName]))
                else:
                    return w
        except:
            pass
    try:
        for w in QtGui.qApp.topLevelWidgets():
            for c in w.children():
                if c.objectName() == Name:
                    if LongName:
                        return (c, "|" + "|".join([str(w.objectName()),
                                             str(c.objectName())]))
                    else:
                        return c
    except:
        pass


def UIExists(Name, AsBool=True):
    '''
    Simple wrapper that will search both long and short names of UI's.  Good if the window
    has become docked.

    :param Name: Name of the UI we're looking for.  Can be the shortName or fullaName.
    :Returns: `QObject` or a `bool` based on AsBool parameter.
    '''

    QObject = GetQtWidget(Name)
    if QObject:
        if AsBool:
            return bool(QObject)
        return QObject
    else:
        if AsBool:
            return False
        return None


def Raise(Name):
    '''
    Based on the long or shortName this will find the QObject and call QObject.raise_()
    '''
    QObject = GetQtWidget(Name)
    if QObject:
        QObject.setHidden(False)
        QObject.raise_()
        return True
    else:
        return False


def getQtElement(elementString, guiTarget, LongName=False):
	""" 
	Finds any ui element within the given target
	
	Input: 	elementString: 'str' of the QObject
			guiTarget: 'str' of the UI to search within
			
	Note: If you've made the window dock-able inside Maya, pass the dockControl name	
	"""
	
	qSearch = GetQtWidget(guiTarget)
	for a in qSearch.findChildren(QtGui.QWidget):
		if a.objectName() == elementString:
			if LongName:
				return GetFullName(a)
			else:
				return a