from objc_util import *
import sceneKit as scn
import ui
import math
import random
from enum import Enum
import weakref
import os
from car import Car
from cars_properties import cars_properties
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="debug.log", encoding="utf-8", level=logging.DEBUG)

db = scn.DebugOption
debug_options = db.ShowPhysicsShapes  # | db.RenderAsWireframe


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
        self.scene.physicsWorld.contactDelegate = self
        self.scn_view.scene = self.scene

        self.scene.rootNode.addChildNode(self.make_floor())

        self.scene.rootNode.addChildNode(self.make_camera())

        self.scene.rootNode.addChildNode(self.make_lights())

        self.cars = [
            Car(scene=self.scene, properties=a_car_properties, simple=True)
            for a_car_properties in cars_properties
        ]

        self.close_button = self.make_close_button()
        self.close_button.action = self.close_button_action
        self.ui_view.add_subview(self.close_button)

        self.is_close_button_clicked = False
        self.is_shutting_down = False

        self.main_view.present(style="fullscreen", hide_title_bar=True)

    def make_ui_view(self, w, h):
        ui_view = ui.View()
        ui_view.frame = (0, 0, w, h)
        ui_view.name = "vehicle demo"
        return ui_view

    def make_close_button(self):
        close_button = ui.Button()
        close_button.frame = (20, 40, 40, 40)
        close_button.background_image = ui.Image.named("emj:No_Entry_2")
        close_button.action = self.close_button_action
        return close_button

    def make_scn_view(self, ui_view):
        scn_view = scn.View(frame=ui_view.bounds, superView=ui_view)
        scn_view.preferredFramesPerSecond = 30
        scn_view.debugOptions = debug_options
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
        camera_node.position = scn.Vector3(10, 10, 30)
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

    def close_button_action(self, sender):
        self.is_close_button_clicked = True
        self.ui_view.remove_subview(self.close_button)

    def shutdown(self):
        self.is_shutting_down = True
        for car in self.cars:
            car.shutdown()
        self.ui_view.close()

    def update(self, renderer, time):
        if self.is_close_button_clicked:
            if not self.is_shutting_down:
                self.shutdown()
            return

        for car in self.cars:
            car.control()


Demo.run()
