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

        self.ui_view.present("full_screen")

    def make_ui_view(self, w, h):
        ui_view = ui.View()
        ui_view.frame = (0, 0, w, h)
        ui_view.name = "vehicle demo"
        return ui_view

    def make_scn_view(self, ui_view):
        scn_view = scn.View(frame=ui_view.bounds, superView=ui_view)
        scn_view.preferredFramesPerSecond = 30
        # scn_view.debugOptions = db.ShowPhysicsShapes
        scn_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        scn_view.allowsCameraControl = True
        scn_view.showsStatistics = True
        scn_view.backgroundColor = (0.77, 0.97, 1.0)
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
        self.car.control()


class Car(scn.Node):
    def control(self):
        self.physics_vehicle.applyEngineForce(1000, 0)

    def __init__(self, scene: scn.Scene):
        super().__init__()

        scene.rootNode.addChildNode(self)
        self.position = (0, 10, 10)

        self.body = self.add_body_without_wheels()
        self.wheels = self.build_and_attach_wheels()

        physicsBody = scn.PhysicsBody.dynamicBody()
        physicsBody.allowsResting = False
        physicsBody.mass = 1200
        physicsBody.restitution = 0.1
        physicsBody.damping = 0.3
        physicsBody.physicsShape = scn.PhysicsShape(self)
        self.physicsBody = physicsBody

        physics_wheels = [scn.PhysicsVehicleWheel(node=wheel) for wheel in self.wheels]

        self.physics_vehicle = scn.PhysicsVehicle(
            chassisBody=self.physicsBody, wheels=physics_wheels
        )
        scene.physicsWorld.addBehavior(self.physics_vehicle)

    def add_body_without_wheels(self):
        body_material = scn.Material()
        body_material.diffuse.contents = "#ff0000"
        body_material.specular.contents = (0.88, 0.88, 0.88)

        body = scn.Box(2, 1, 4, 0.2)
        body.firstMaterial = body_material

        body_node = scn.Node.nodeWithGeometry(body)
        body_node.position = (0, 0.75, 0)

        top = scn.Box(1.6, 0.6, 1.8, 0.1)
        top.firstMaterial = body_material
        top_node = scn.Node.nodeWithGeometry(top)
        top_node.position = (0, 0.5 + 0.2, 0)
        body_node.addChildNode(top_node)

        door1 = scn.Box(2.02, 1 - 0.2, 1.8 / 2.2, 0.08)
        door1.firstMaterial = body_material
        door1_node = scn.Node.nodeWithGeometry(door1)
        door1_node.position = (0, 0.1, 1.8 / 4)
        body_node.addChildNode(door1_node)

        door2_node = scn.Node.nodeWithGeometry(door1)
        door2_node.position = (0, 0.1, -1.8 / 4 + 0.1)
        body_node.addChildNode(door2_node)

        window_material = scn.Material()
        window_material.diffuse.contents = (0.64, 0.71, 0.75, 0.6)
        window_material.specular.contents = (0.88, 0.88, 0.88, 0.8)

        sideW1 = scn.Box(1.61, 0.6 - 0.1, 1.8 / 2.2, 0.08)
        sideW1.firstMaterial = window_material
        sideW1_node = scn.Node.nodeWithGeometry(sideW1)
        sideW1_node.position = (0, 0.5 + 0.2, 1.8 / 4)
        body_node.addChildNode(sideW1_node)

        sideW2_node = scn.Node.nodeWithGeometry(sideW1)
        sideW2_node.position = (0, 0.5 + 0.2, -1.8 / 4 + 0.1)
        body_node.addChildNode(sideW2_node)

        window_materials = [scn.Material() for i in range(6)]
        window_materials[0] = window_material
        window_materials[2] = window_material
        for i in [1, 3, 4, 5]:
            window_materials[i] = body_material

        alpha = math.pi / 5
        frontW = scn.Box(1.4, 0.6 / math.cos(alpha), 0.1, 0.06)
        frontW.materials = window_materials
        frontW_node = scn.Node.nodeWithGeometry(frontW)
        frontW_node.position = (
            0,
            0.5 + 0.2 - 0.05,
            1.8 / 2 + math.tan(alpha) * 0.6 / 2 - 0.1,
        )
        frontW_node.rotation = (1, 0, 0, -alpha)
        body_node.addChildNode(frontW_node)

        alpha = math.pi / 5
        frontW2 = scn.Box(1.3, 0.6 / math.cos(alpha), 0.3, 0.0)
        frontW2.firstMaterial = window_material
        frontW2_node = scn.Node.nodeWithGeometry(frontW2)
        frontW2_node.position = (
            0,
            0.5 + 0.2 - 0.05 - 0.2,
            1.8 / 2 + math.tan(alpha) * 0.6 / 2 - 0.08,
        )
        frontW2_node.rotation = (1, 0, 0, -alpha)
        body_node.addChildNode(frontW2_node)

        alpha = math.pi / 3.2
        rearW = scn.Box(1.4, 0.6 / math.cos(alpha), 0.2, 0.2)
        rearW.materials = window_materials
        rearW_node = scn.Node.nodeWithGeometry(rearW)
        rearW_node.position = (
            0,
            0.5 + 0.2 - 0.0417,
            -1.8 / 2 - math.tan(alpha) * 0.6 / 2 + 0.15,
        )
        rearW_node.rotation = (1, 0, 0, alpha)
        body_node.addChildNode(rearW_node)

        alpha = math.pi / 3.2
        rearW2 = scn.Box(1.3, 0.6 / math.cos(alpha), 0.3, 0.05)
        rearW2.firstMaterial = window_material
        rearW2_node = scn.Node.nodeWithGeometry(rearW2)
        rearW2_node.position = (
            0,
            0.5 + 0.2 - 0.05 - 0.2,
            -1.8 / 2 - math.tan(alpha) * 0.6 / 2 + 0.1,
        )
        rearW2_node.rotation = (1, 0, 0, alpha)
        body_node.addChildNode(rearW2_node)

        nose = scn.Pyramid(2 - 0.4, 0.15, 1 - 0.2)
        nose.firstMaterial = body_material
        nose_node = scn.Node.nodeWithGeometry(nose)
        nose_node.position = (0, 0, 2 - 0.03)
        nose_node.rotation = (1, 0, 0, math.pi / 2)
        body_node.addChildNode(nose_node)

        lampBack_colors = [(0.6, 0.0, 0.0), (1.0, 0.0, 0.0)]

        front_spot = scn.Light()
        front_spot.type = scn.LightTypeSpot
        front_spot.castsShadow = False
        front_spot.color = (1.0, 1.0, 0.95)
        front_spot.spotInnerAngle = 20
        front_spot.spotOuterAngle = 25
        front_spot.attenuationEndDistance = 15

        exhaust = scn.Tube(0.05, 0.07, 0.08)
        exhaust.firstMaterial.metalness.contents = (0.5, 0.5, 0.5)
        exhaust_node = scn.Node.nodeWithGeometry(exhaust)
        exhaust_node.position = (0.5, -0.42, -2.04)
        exhaust_node.rotation = (1, 0, 0, math.pi / 2)
        body_node.addChildNode(exhaust_node)

        lamp = scn.Tube(0.12, 0.15, 4.07)
        lamp.firstMaterial.metalness.contents = (0.93, 0.93, 0.93)
        lampGlasFront = scn.Sphere(0.13)
        lampGlasFront.firstMaterial.emission.contents = (0.92, 0.93, 0.66)
        lampGlasBack = scn.Sphere(0.13)
        lampGlasBack.firstMaterial.diffuse.contents = "black"
        lampGlasBack.firstMaterial.emission.contents = lampBack_colors[0]

        lamp_nodeR = scn.Node.nodeWithGeometry(lamp)
        lamp_nodeR.position = (-0.6, 0, 0.015)
        lamp_nodeR.rotation = (1, 0, 0, math.pi / 2)
        body_node.addChildNode(lamp_nodeR)
        lamp_nodeL = scn.Node.nodeWithGeometry(lamp)
        lamp_nodeL.position = (0.6, 0, 0.015)
        lamp_nodeL.rotation = (1, 0, 0, math.pi / 2)
        body_node.addChildNode(lamp_nodeL)

        lampGlasFront_nodeR = scn.Node.nodeWithGeometry(lampGlasFront)
        lampGlasFront_nodeR.position = (0, 1.95, 0)
        lampGlasFront_nodeR.lookAt((0, 45, 10))
        lampGlasFront_nodeR.light = front_spot
        lamp_nodeR.addChildNode(lampGlasFront_nodeR)
        lampGlasBack_nodeR = scn.Node.nodeWithGeometry(lampGlasBack)
        lampGlasBack_nodeR.position = (0, -1.95, 0)
        lamp_nodeR.addChildNode(lampGlasBack_nodeR)

        lampGlasFront_nodeL = scn.Node.nodeWithGeometry(lampGlasFront)
        lampGlasFront_nodeL.position = (0, 1.95, 0)
        lampGlasFront_nodeL.lookAt((0, 45, 10))
        lampGlasFront_nodeL.light = front_spot
        lamp_nodeL.addChildNode(lampGlasFront_nodeL)
        lampGlasBack_nodeL = scn.Node.nodeWithGeometry(lampGlasBack)
        lampGlasBack_nodeL.position = (0, -1.95, 0)
        lamp_nodeL.addChildNode(lampGlasBack_nodeL)

        self.addChildNode(body_node)
        return body_node

    def build_and_attach_wheels(self):

        tire = scn.Tube(0.12, 0.35, 0.25)
        tire.firstMaterial.diffuse.contents = "black"
        tire_node = scn.Node.nodeWithGeometry(tire)

        rim = scn.Cylinder(0.14, 0.1)
        rim.firstMaterial.diffuse.contents = "gray"
        rim.firstMaterial.specular.contents = (0.88, 0.88, 0.88)
        rim_node = scn.Node.nodeWithGeometry(rim)
        rim_node.name = "rim"
        rim_node.position = (0, 0.06, 0)

        rim_deco = scn.Text("Y", 0.05)
        rim_deco.font = ("Arial Rounded MT Bold", 0.3)
        rim_deco.firstMaterial.diffuse.contents = "black"
        rim_deco.firstMaterial.specular.contents = (0.88, 0.88, 0.88)
        rim_deco_node = scn.Node.nodeWithGeometry(rim_deco)
        rim_deco_node.name = "deco"
        rim_deco_node.position = (-0.1, 0.03, -1.12)
        rim_deco_node.rotation = (1, 0, 0, math.pi / 2)
        # rim_node.addChildNode(rim_deco_node)

        # base wheel is tire+rim+rim deco lying flat
        base_wheel_node = scn.Node()
        base_wheel_node.addChildNode(tire_node)
        base_wheel_node.addChildNode(rim_node)
        base_wheel_node.addChildNode(rim_deco_node)
        base_wheel_node.name = "base-wheel"

        wheel_nodes = [scn.Node()]

        # left front wheel
        wheel_nodes[0].addChildNode(base_wheel_node)
        wheel_nodes[0].position = (0.94, 0.4, 2 - 0.6)
        wheel_nodes[0].childNodeWithName("base-wheel", True).rotation = (
            0,
            0,
            1,
            -math.pi / 2,
        )

        # right front wheel
        wheel_nodes.append(wheel_nodes[0].clone())
        wheel_nodes[1].position = (-0.94, 0.4, 2 - 0.6)
        wheel_nodes[1].childNodeWithName("base-wheel", True).rotation = (
            0,
            0,
            1,
            +math.pi / 2,
        )

        wheel_nodes.append(wheel_nodes[0].clone())
        wheel_nodes[2].position = (0.94, 0.4, -2 + 0.7)
        wheel_nodes[2].childNodeWithName("base-wheel", True).rotation = (
            0,
            0,
            1,
            -math.pi / 2,
        )

        wheel_nodes.append(wheel_nodes[0].clone())
        wheel_nodes[3].position = (-0.94, 0.4, -2 + 0.7)
        wheel_nodes[3].childNodeWithName("base-wheel", True).rotation = (
            0,
            0,
            1,
            +math.pi / 2,
        )

        for wheel in wheel_nodes:
            self.addChildNode(wheel)

        return wheel_nodes


Demo.run()
