import sceneKit as scn
from objc_util import *
import sceneKit as scn
import ui
import math
import random
from enum import Enum
import weakref
import os

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

class db(Enum):
    OptionNone = scn.DebugOption.OptionNone,
    ShowBoundingBoxes = scn.DebugOption.ShowBoundingBoxes,
    ShowWireframe = scn.DebugOption.ShowWireframe,
    RenderAsWireframe = scn.DebugOption.RenderAsWireframe,
    ShowSkeletons = scn.DebugOption.ShowSkeletons,
    ShowCreases = scn.DebugOption.ShowCreases,
    ShowConstraints = scn.DebugOption.ShowConstraints,
    ShowCameras = scn.DebugOption.ShowCameras,
    ShowLightInfluence = scn.DebugOption.ShowLightInfluences,
    ShowLightExtents = scn.DebugOption.ShowLightExtents,
    ShowPhysicsShapes = scn.DebugOption.ShowPhysicsShapes,
    ShowPhysicsField = scn.DebugOption.ShowPhysicsFields


class Demo():
    @classmethod
    def run(cls):
        cls()


    def __init__(self):
        w, h = ui.get_window_size()

        self.ui_view = self.make_ui_view(w, h)

        self.scn_view = self.make_scn_view(w, h)
        self.ui_view.add_subview(self.scn_view)
        self.scn_view.delegate = self
        
        self.scene = self.make_scene()
        self.scn_view.scene = self.scene
        self.scene.physicsWorld.contactDelegate = self

        self.ui_view.present('full_screen', hide_title_bar=True)


    def make_ui_view(self, w, h):
        ui_view = ui.View()
        
        ui_view.frame = (0, 0, w, h)
        ui_view.name = "vehicle demo"
        
        return ui_view
    
    def make_scn_view(self, w, h):
        scn_view = scn.View()
        scn_view.preferredFramesPerSecond = 30
        scn_view.debugOptions = db.ShowPhysicsShapes

        scn_view.frame = (0, 0, w, h)
        scn_view.autoresizingMask = (scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth)
        scn_view.allowsCameraControl = True
        scn_view.showsStatistics = True
        scn_view.backgroundColor = (0.77, 0.97, 1.0)
        
        return scn_view
    
    def make_scene(self):
        scene = scn.Scene()
        
        return scene
    

    def update(self, renderer, time):
        pass


Demo.run()