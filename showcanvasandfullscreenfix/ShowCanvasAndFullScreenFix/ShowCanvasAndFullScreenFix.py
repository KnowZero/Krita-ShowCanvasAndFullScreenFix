from krita import *
import json


class ShowCanvasAndFullScreenFix(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        
        settingsData = Krita.instance().readSetting("", "showCanvasAndFullScreenFixPlugin","")
        if settingsData.startswith('{'):
            self.settings = json.loads(settingsData)

        else:
            self.settings = {
                'enabled': 0,
                'timeout': 200
            }
        
        self.notify = Krita.instance().notifier()
        self.notify.setActive(True)
        self.notify.windowCreated.connect(self.windowCreatedSetup)
        
        self.actionList = ['view_show_canvas_only','fullscreen','view_toggledockers']


    def createActions(self, window):
        self.qwin = window.qwindow()
        
        self.action = window.createAction("showCanvasAndFullScreenFixPlugin", "Show-Canvas And Full-Screen Fix", "tools/scripts")
        
        menu = QMenu("showCanvasAndFullScreenFixPlugin", window.qwindow())
        self.action.setMenu(menu)
        
        self.subaction1 = window.createAction("showCanvasAndFullScreenFixPluginEnable", "Enable", "tools/scripts/showCanvasAndFullScreenFixPlugin")
        self.subaction1.setCheckable(True)
        self.subaction1.toggled.connect(self.slotToggleEnable)
        
        subaction2 = window.createAction("showCanvasAndFullScreenFixPluginConfig", "Configure...", "tools/scripts/showCanvasAndFullScreenFixPlugin")
        subaction2.triggered.connect(self.slotOpenConfig)
        

    def slotOpenConfig(self):
        timeout, ok = QInputDialog.getInt(None,"Timeout",
                                                        "Set cover dialog fade in and fade out timeout in miliseconds: (0 = disabled)", 
                                                        self.settings['timeout'],0,10000)
        if (ok):
            self.settings['timeout'] = timeout
            Krita.instance().writeSetting("", "showCanvasAndFullScreenFixPlugin",json.dumps(self.settings))
    
    def slotToggleEnable(self, toggle):
        print ("TOGGLE!", toggle)
        
        self.settings['enabled'] = 1 if toggle else 0
        Krita.instance().writeSetting("", "showCanvasAndFullScreenFixPlugin",json.dumps(self.settings))
        
        for actionName in self.actionList:
            if toggle:
                Krita.instance().action(actionName).installEventFilter(self)
            else:
                Krita.instance().action(actionName).removeEventFilter(self)
        
        

            
    
    
    def windowCreatedSetup(self):
        self.cover = self.coverWidget(self.qwin)
        
        if self.settings['enabled'] == 1:
            self.subaction1.setChecked(True)

    def eventFilter(self, obj, event):
        ev = event.type()

        if ev == QEvent.Shortcut:
            currentAction = None
            for actionName in self.actionList:
                for shortcut in Krita.instance().action(actionName).shortcuts():
                    if shortcut == event.key():
                        self.cover.startCover(actionName, self.settings)
                        return True


        return False

    def setup(self):
        pass


    class coverWidget(QWidget):
        def __init__(self, window, parent=None):
            super().__init__(parent)
            

            
            self.qwin = window
            self.mdi = self.qwin.findChild(QMdiArea)

            
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip | Qt.WindowTransparentForInput)
            self.setFocusPolicy(Qt.NoFocus);
            self.setAttribute(Qt.WA_ShowWithoutActivating)
            
            
            self.setAutoFillBackground(True)
            

            self.timerId = 0
            self.runTime = 0
            
            self.running = QMutex()
            
            
        def paintEvent(self, event):
            painter = QPainter()
            painter.begin(self)
            painter.drawPixmap(self.drawGeometry, self.targetWidgetPixelData)
            painter.end()
            
        def timerEvent(self, event):
            if event.timerId() == self.timerId:
                self.runTime += 1
                
                if self.runTime == self.settings['timeout']:
                    #print ("SHOW!", self.timerId )
                    Krita.instance().action(self.currentAction).trigger()
                    
                    qApp.processEvents(QEventLoop.ExcludeUserInputEvents)
                elif self.runTime == self.settings['timeout'] * 2:
                    #print ("KILLED!", self.timerId )
                    self.killTimer(self.timerId)
                    
                    self.mdi.removeEventFilter(self)
                    
                    self.hide()
                    self.verifyPos()
                    self.running.unlock()
                elif self.runTime % 50 == 0:
                    #print ("PAINT!")
                    self.refreshTarget()
                    self.update()

            
        
        def preloadInitialState(self):
            canvasColor = Krita.instance().readSetting('','canvasBorderColor','128,128,128')
            self.useMdiPal = True
            self.mdiStartPos = self.mdi.mapToGlobal(QPoint())
            
            self.mdiSubWindowList = []
            self.subwinStartPos = []
            self.mdiMaximizedList = []
            self.mdiScrollAreaList = []

            for subwin in self.mdi.subWindowList():
                view = subwin.widget()

                self.mdiSubWindowList.append(subwin)
                self.mdiMaximizedList.append(subwin.isMaximized())
                self.mdiScrollAreaList.append(view.findChild(QAbstractScrollArea))


                if self.mdi.viewMode() == QMdiArea.SubWindowView and not self.mdiMaximizedList[-1]:
                    self.subwinStartPos.append(subwin.mapToGlobal(QPoint()))
                else:
                    self.subwinStartPos.append(QPoint(
                        self.mdiScrollAreaList[-1].horizontalScrollBar().value(),
                        self.mdiScrollAreaList[-1].verticalScrollBar().value()
                    ))
                    self.useMdiPal = False
                    
            pal = QPalette()
            pal.setColor(QPalette.Window, self.mdi.background().color() if self.useMdiPal else QColor(*map(int, canvasColor.split(','))))
            self.setPalette(pal)
        
        def refreshTarget(self):
            self.targetWidgetPixelData = self.targetWidget.grab()
            targetPos = self.targetWidget.mapToGlobal(QPoint()) if self.hideTitle else self.targetWidget.mapTo(self.qwin,QPoint())
            self.drawGeometry = QRect( targetPos.x(),  targetPos.y(), self.targetWidget.width(), self.targetWidget.height())
        
        def startCover(self, currentAction, settings):
            self.settings = settings
            #print ("START!", self.settings)
            if self.running.tryLock(self.settings['timeout']*2):
                self.currentAction = currentAction
                self.preloadInitialState()
                
                self.currentSubWindow = self.mdi.currentSubWindow()
                self.targetWidget = self.currentSubWindow.findChild(QOpenGLWidget) if self.mdi.viewMode() == QMdiArea.TabbedView or self.currentSubWindow.isMaximized() else self.mdi
                
                self.hideTitle = Krita.instance().readSetting('','hideTitleBarFullscreen','true') == 'true'
                if self.currentAction == 'view_toggledockers':
                    self.hideTitle = False
                
                s = qApp.screenAt(self.qwin.pos()) if self.hideTitle else self.qwin
                r = s.geometry()
                self.setGeometry(r)
                self.refreshTarget()
                
                self.mdi.installEventFilter(self)
                self.runTime = 0
                if self.settings['timeout'] > 0:
                    self.show()
                    self.timerId = self.startTimer(1)
                    #print ("RUN!", self.timerId )
                else:
                    Krita.instance().action(self.currentAction).trigger()
                    qApp.processEvents(QEventLoop.ExcludeUserInputEvents)
                    self.mdi.removeEventFilter(self)
                    self.verifyPos()
                    self.running.unlock()
                

        
        
        def verifyPos(self):
            pass
                    
        
        def syncPos(self):
            mdiPos = self.mdi.mapToGlobal(QPoint())

            for i in range(len(self.mdiSubWindowList)):
                if self.mdi.viewMode() == QMdiArea.SubWindowView and not self.mdiMaximizedList[i]:
                    self.mdiSubWindowList[i].move(self.subwinStartPos[i] - mdiPos)
                else:
                    self.mdiScrollAreaList[i].horizontalScrollBar().setValue(-self.mdiStartPos.x() + mdiPos.x() + self.subwinStartPos[i].x() )
                    self.mdiScrollAreaList[i].verticalScrollBar().setValue(-self.mdiStartPos.y() + mdiPos.y() + self.subwinStartPos[i].y() )
            
        def eventFilter(self, obj, event):
            ev = event.type()
            if ev == QEvent.Move:
                self.syncPos()
            return False


app = Krita.instance()
extension = ShowCanvasAndFullScreenFix(parent=app)
app.addExtension(extension)
    
