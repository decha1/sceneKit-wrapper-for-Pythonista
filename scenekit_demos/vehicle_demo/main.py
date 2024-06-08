"""

"""

from objc_util import *
import sceneKit as scn
import ui
import math
import random
from enum import Enum
import weakref
import os
from car import Car
from car import CarProgram
from cars_properties import cars_properties
import logging
import time

IS_SIMPLE = False

logger = logging.getLogger(__name__)
logging.basicConfig(filename="debug.log", encoding="utf-8", level=logging.DEBUG)

db = scn.DebugOption
debug_options = db.ShowPhysicsShapes #  | db.RenderAsWireframe


def length(a):
    return math.sqrt(sum(x**2 for x in a))


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

        self.floor_node = self.make_floor()
        self.scene.rootNode.addChildNode(self.floor_node)

        self.camera_node = self.make_camera()
        self.scene.rootNode.addChildNode(self.camera_node)

        self.scene.rootNode.addChildNode(self.make_lights())

        self.cars = [
            Car(scene=self.scene, properties=a_car_properties, simple=IS_SIMPLE)
            for a_car_properties in cars_properties
        ]

        self.close_button = self.make_close_button()
        self.close_button.action = self.close_button_action
        self.ui_view.add_subview(self.close_button)

        self.is_close_button_clicked = False
        self.is_shutting_down = False

        self.ui_view.present(style="fullscreen", hide_title_bar=True)

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
        # next line prevents multiple clicks of close button, not sure if necessary?
        # self.ui_view.remove_subview(self.close_button)

        # trigger shutdown during next render update
        self.is_close_button_clicked = True

    def shutdown(self):
        self.is_shutting_down = True

        # don't know if the following pause statements actually do anything
        self.scene.paused = True
        self.scn_view.pause()

        for car in self.cars:
            car.shutdown()
        self.ui_view.close()

    def update(self, view, time):
        # update continues to be called even if scene or scene_view is paused
        if self.is_close_button_clicked:
            # run shutdown only once, if already running, do not run again
            if not self.is_shutting_down:
                self.shutdown()
            return
        
        if IS_SIMPLE:
            angle = 0.1
            multiplier = 1
            for i, car in enumerate(self.cars):
                car.physics_vehicle.setSteeringAngle(angle * i, 0)
                car.physics_vehicle.setSteeringAngle(angle * i, 1)
                car.physics_vehicle.applyEngineForce(multiplier * 950, 0)
                car.physics_vehicle.applyEngineForce(multiplier * 950, 1)
                car.physics_vehicle.applyBrakingForce(0, 2)
                car.physics_vehicle.applyBrakingForce(0, 3)
            return
            
        cx, cz, node_dist = 0.0, 0.0, 99999999999.0
        camPos = self.camera_node.position
        for car in self.cars:
            car.current_speed = abs(car.physics_vehicle.speedInKilometersPerHour)

            car_position = car.presentationNode.position

            cx += car_position.x
            cz += car_position.z
            node_dist = min(node_dist, abs(car_position.z - camPos.z))

            if (
                car.current_program == CarProgram.reverse
                or car.current_program == CarProgram.obstacle
            ):
                pass
            else:
                obstacles = list(
                    view.nodesInsideFrustumWithPointOfView(car.camera.presentationNode)
                )
                try:
                    obstacles.remove(self.floor_node)
                except ValueError:
                    pass
                if len(obstacles) > 0:
                    car.setProgram(CarProgram.obstacle)

                elif length(car_position) > random.uniform(
                    car.too_far_distance, car.too_far_distance + 30
                ):
                    car.setProgram(CarProgram.turn_back)

            # the car.move method does not seem to use view or atTime, considere rewriting
            #car.move(view, atTime)
            car.move(None, None)  # test to see if above is correct

        self.camera_node.lookAt((cx / len(self.cars), camPos.y, cz / len(self.cars)))
        if sum(
            1
            for car in self.cars
            if view.isNodeInsideFrustum(car.presentationNode, self.camera_node)
        ) < len(self.cars):
            self.camera_node.position = (camPos.x, camPos.y, camPos.z + 0.1)
        elif node_dist < 15:
            self.camera_node.position = (camPos.x, camPos.y, camPos.z + 0.05)
        elif node_dist > 35:
            self.camera_node.position = (camPos.x, camPos.y, camPos.z - 0.03)


Demo.run()
