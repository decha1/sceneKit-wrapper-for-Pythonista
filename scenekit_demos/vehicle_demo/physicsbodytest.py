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
logging.basicConfig(filename="debug.log", encoding="utf-8", level=logging.DEBUG)

db = scn.DebugOption


class Demo:
    @classmethod
    def run(cls):
        cls()

    def __init__(self):
        w, h = ui.get_window_size()

        self.ui_view = self.make_ui_view(w, h)

        self.scn_view = self.make_scn_view(self.ui_view)
        self.scn_view.delegate = self

        self.scene = self.make_scene()
        self.scn_view.scene = self.scene
        self.scene.physicsWorld.contactDelegate = self

        self.floor = self.make_floor()
        self.scene.rootNode.addChildNode(self.floor)

        self.camera = self.make_camera()
        self.scene.rootNode.addChildNode(self.camera)

        self.lights = self.make_lights()
        self.scene.rootNode.addChildNode(self.lights)

        self.car = Car(self.scene)

        """ 

            
        physicsBody = scn.PhysicsBody.dynamicBody()
        #physicsBody.allowsResting = False
        physicsBody.mass = 1200
        physicsBody.restitution = 0.1
        physicsBody.damping = 0.3
        #physicsBody.physicsShape = scn.PhysicsShape(self)
        b.physicsBody = physicsBody
        
        
        
        wheel_nodes = [self.make_box(1,(5,0,5)),
                        self.make_box(1,(5,0,-5)),
                        self.make_box(1,(-5,0,5)),
                        self.make_box(1,(-5,0,-5)),
                        self.make_box(1,(8,0,8))
                        ]
        
        for w in wheel_nodes:
            w.eulerAngles = (0,0,math.pi)
        physicsWheels= map(scn.PhysicsVehicleWheel, wheel_nodes)
        
        self.vehicle = scn.PhysicsVehicle(physicsBody,physicsWheels)
        #print(self.vehicle)
        self.scene.physicsWorld.addBehavior(self.vehicle)
        
        """
        self.ui_view.present("full_screen")

    def make_box(self, size, position):
        geometry = scn.Box(size, size, size)
        r = scn.Material()
        r.diffuse.contents = "red"
        b = scn.Material()
        b.diffuse.contents = "blue"
        g = scn.Material()
        g.diffuse.contents = "green"
        lg = scn.Material()
        lg.diffuse.contents = "lightgrey"
        geometry.materials = [b, r, lg, lg, g, lg]
        n = scn.Node.nodeWithGeometry(geometry)

        q = scn.Node()
        q.position = position
        q.addChildNode(n)
        self.scene.rootNode.addChildNode(q)
        return q

    def make_ui_view(self, w, h):
        ui_view = ui.View()
        ui_view.frame = (0, 0, w, h)
        ui_view.name = "vehicle demo"
        return ui_view

    def make_scn_view(self, ui_view):
        scn_view = scn.View(frame=ui_view.bounds, superView=ui_view)
        scn_view.preferredFramesPerSecond = 30
        scn_view.debugOptions = db.ShowPhysicsShapes  # | db.RenderAsWireframe
        scn_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        scn_view.allowsCameraControl = True
        scn_view.showsStatistics = True
        scn_view.backgroundColor = "black"
        return scn_view

    def make_scene(self):
        scene = scn.Scene()
        return scene

    def make_floor(self):
        floor_geometry = scn.Floor()
        floor_geometry.reflectivity = 0.05
        tile_image = ui.Image.named("plf:Ground_DirtCenter")
        tile_number = 5
        # fmt: off
        tile_factor = scn.Matrix4(
            tile_number, 0.0, 0.0,  0.0,
            0.0, tile_number, 0.0, 0.0,
            0.0, 0.0, tile_number, 0.0,
            0.0, 0.0, 0.0, 1.0,
        )
        # fmt: on

        floor_geometry.firstMaterial.diffuse.contents = tile_image
        floor_geometry.firstMaterial.diffuse.intensity = 0.8
        floor_geometry.firstMaterial.diffuse.contentsTransform = tile_factor

        floor_geometry.firstMaterial.diffuse.wrapS = scn.WrapMode.Repeat
        floor_geometry.firstMaterial.diffuse.wrapT = scn.WrapMode.Repeat

        floor_geometry.firstMaterial.locksAmbientWithDiffuse = True
        floor_node = scn.Node.nodeWithGeometry(floor_geometry)
        floor_node.name = "Floor"
        floor_node.physicsBody = scn.PhysicsBody.staticBody()
        return floor_node

    def make_camera(self):
        camera_node = scn.Node()
        camera_node.camera = scn.Camera()
        camera_node.camera.zFar = 150
        camera_node.position = scn.Vector3(5, 10, 30)
        return camera_node

    def make_lights(self):
        all_lights_node = scn.Node()

        light_node = scn.Node()
        light_node.position = (50, 50, 50)
        light_node.lookAt((0, 0, 0))
        light = scn.Light()
        light.type = scn.LightTypeDirectional
        light.castsShadow = True
        light.shadowSampleCount = 16
        light.color = (0.95, 1.0, 0.98)
        light_node.light = light
        all_lights_node.addChildNode(light_node)

        ambient_node = scn.Node()
        ambient = scn.Light()
        ambient.type = scn.LightTypeAmbient
        ambient.color = (0.38, 0.42, 0.45, 0.1)
        ambient_node.light = ambient
        all_lights_node.addChildNode(ambient_node)

        return all_lights_node

    def update(self, renderer, time):
        # return
        self.car.control()
        # self.vehicle.applyEngineForce(1000)


Demo.run()
