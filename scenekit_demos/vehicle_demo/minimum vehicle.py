import sceneKit as scn
from objc_util import *
import sceneKit as scn
import ui
import math
import random
from enum import IntEnum
import weakref
import os

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

DEBUG = False
MAXCARS = 3  # max 5, set it lower for weaker devices
ENGINESOUND = True  # set it to False for weaker devices or if too many cars
MAXACTIVEREVERSE = 2

UIDevice = ObjCClass("UIDevice")
device = UIDevice.currentDevice()
machine = os.uname().machine
system_version = int(str(device.systemVersion()).split(".")[0])
WORLD_SPEED = 1.0 if system_version >= 13 else 2.0


class Demo:
    @classmethod
    def run(cls):
        cls().main()

    @on_main_thread
    def main(self):
        self.main_view = ui.View()
        w, h = ui.get_window_size()
        self.main_view.frame = (0, 0, w, h)
        self.main_view.name = "vehicle demo"

        self.close_button = ui.Button()
        self.close_button.action = self.close
        self.close_button.frame = (20, 40, 40, 40)
        self.close_button.background_image = ui.Image.named("emj:No_Entry_2")

        self.scene_view = scn.View((0, 0, w, h), superView=self.main_view)
        self.scene_view.preferredFramesPerSecond = 30

        self.scene_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        self.scene_view.allowsCameraControl = True

        self.scene_view.scene = scn.Scene()
        self.root_node = self.scene_view.scene.rootNode

        self.scene_view.backgroundColor = (0.77, 0.97, 1.0)
        self.scene_view.delegate = self

        self.physics_world = self.scene_view.scene.physicsWorld
        self.physics_world.speed = WORLD_SPEED
        self.physics_world.contactDelegate = self

        floor_geometry = scn.Floor()
        floor_geometry.reflectivity = 0.05
        tile_image = ui.Image.named("plf:Ground_DirtCenter")
        tile_number = 5
        tile_factor = scn.Matrix4(
            tile_number,
            0.0,
            0.0,
            0.0,
            0.0,
            tile_number,
            0.0,
            0.0,
            0.0,
            0.0,
            tile_number,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
        )

        floor_geometry.firstMaterial.diffuse.contents = tile_image
        floor_geometry.firstMaterial.diffuse.intensity = 0.8
        floor_geometry.firstMaterial.diffuse.contentsTransform = tile_factor

        (
            floor_geometry.firstMaterial.diffuse.wrapS,
            floor_geometry.firstMaterial.diffuse.wrapT,
        ) = (scn.WrapMode.Repeat, scn.WrapMode.Repeat)

        floor_geometry.firstMaterial.locksAmbientWithDiffuse = True
        self.floor_node = scn.Node.nodeWithGeometry(floor_geometry)
        self.floor_node.name = "Floor"
        self.floor_node.physicsBody = scn.PhysicsBody.staticBody()
        self.root_node.addChildNode(self.floor_node)

        # ---------------------------------------------------------------------------
        # Cars
        self.car = Car(self)
        # ---------------------------------------------------------------------------

        # ---------------------------------------------------------------------------
        # camera
        self.camera_node = scn.Node()
        self.camera_node.camera = scn.Camera()
        self.camera_node.camera.zFar = 150
        # carPos = self.cars[0].node.position
        carPos = scn.Vector3(0, 0, 0)
        self.camera_node.position = scn.Vector3(carPos.x + 5, 10, carPos.z + 30)
        self.root_node.addChildNode(self.camera_node)

        self.light_node = scn.Node()
        self.light_node.position = (50, 50, 50)
        self.light_node.lookAt(self.root_node.position)
        self.light = scn.Light()
        self.light.type = scn.LightTypeDirectional
        self.light.castsShadow = True
        self.light.shadowSampleCount = 16
        self.light.color = (0.95, 1.0, 0.98)
        self.light_node.light = self.light
        self.root_node.addChildNode(self.light_node)

        self.ambient_node = scn.Node()
        self.ambient = scn.Light()
        self.ambient.type = scn.LightTypeAmbient
        self.ambient.color = (0.38, 0.42, 0.45, 0.1)
        self.ambient_node.light = self.ambient
        self.root_node.addChildNode(self.ambient_node)

        self.scene_view.pointOfView = self.camera_node

        self.is_close_button_clicked = False
        self.is_shutting_down = False
        self.main_view.add_subview(self.close_button)
        self.main_view.present(style="fullscreen", hide_title_bar=(not DEBUG))

    def close(self, sender):
        self.is_close_button_clicked = True
        self.main_view.remove_subview(self.close_button)

    def shut_down(self):
        self.is_shutting_down = True
        self.crash_sparks = None
        print("before close")
        self.main_view.close()

    def update(self, view, atTime):
        print("update")
        if self.is_close_button_clicked:
            if not self.is_shutting_down:
                self.shut_down()
            return

        cumulative_car_x = 0.0
        cumulative_car_z = 0.0
        car_camera_min_z_distance = 99999999999.0

        camera_position = self.camera_node.position

        for car in self.cars:
            # set frequently used lookup items to a local variable of the car object ?
            car.current_speed = abs(car.vehicle.speedInKilometersPerHour)
            car.node = car.chassis_node.presentationNode
            car.position = car.node.position

            cumulative_car_x += car.position.x
            cumulative_car_z += car.position.z
            car_camera_min_z_distance = min(
                car_camera_min_z_distance, abs(car.position.z - camera_position.z)
            )

            car.control(0, 10)

        self.camera_node.lookAt(
            (
                cumulative_car_x / len(self.cars),
                camera_position.y,
                cumulative_car_z / len(self.cars),
            )
        )
        if (
            len(
                [
                    view.isNodeInsideFrustum(car.node, self.camera_node)
                    for car in self.cars
                ]
            )
            < len(self.cars) - 1
        ):
            self.camera_node.position = (
                camera_position.x,
                camera_position.y,
                camera_position.z + 0.1,
            )
        elif car_camera_min_z_distance < 15:
            self.camera_node.position = (
                camera_position.x,
                camera_position.y,
                camera_position.z + 0.05,
            )
        elif car_camera_min_z_distance > 35:
            self.camera_node.position = (
                camera_position.x,
                camera_position.y,
                camera_position.z - 0.03,
            )


class Car:
    def __init__(self, world=None, props={}):
        self.world = world
        self.physics_world = world.physics_world
        self.buildCar(
            body_color=props.pop("body_color", (0.6, 0.0, 0.0)),
            sound_file=props.pop("sound", "casino:DiceThrow2"),
            sound_volume=props.pop("volume", 1.0),
        )
        self.chassis_node.position = props.pop("position", (0, 0, 0))
        self.name = props.pop("name", "car")
        self.chassis_node.name = self.name
        # self.program_table = [aProg(self) for aProg in Car.programs]
        # self.current_program = CarProgram.forward
        # self.program_stack = [self.current_program]
        self.brake_light = False
        self.too_far = props.pop("too_far", 30)
        self.current_speed = 0
        self.node = self.chassis_node
        self.position = self.chassis_node.position

    def control(self, angle=0, desired_speed_kmh=0, reverse=False):
        multiplier = -1.2 if reverse else 1
        self.vehicle.setSteeringAngle(angle, 0)
        self.vehicle.setSteeringAngle(angle, 1)

        self.camera_controller_node.rotation = (0, 1, 0, -angle / 2)

        if self.current_speed < desired_speed_kmh:
            self.vehicle.applyEngineForce(multiplier * 950, 0)
            self.vehicle.applyEngineForce(multiplier * 950, 1)
            self.vehicle.applyBrakingForce(0, 2)
            self.vehicle.applyBrakingForce(0, 3)
            self.brakeLights(on=False)
            self.smoke.birthRate = 700 + (desired_speed_kmh - self.current_speed) ** 2.5
        elif self.current_speed > 1.2 * desired_speed_kmh:
            self.vehicle.applyEngineForce(0, 0)
            self.vehicle.applyEngineForce(0, 1)
            self.vehicle.applyBrakingForce(multiplier * 20, 2)
            self.vehicle.applyBrakingForce(multiplier * 20, 3)
            self.brakeLights(on=True)
            self.smoke.birthRate = 0.0
        else:
            self.vehicle.applyEngineForce(0, 0)
            self.vehicle.applyEngineForce(0, 1)
            self.vehicle.applyBrakingForce(0, 2)
            self.vehicle.applyBrakingForce(0, 3)
            self.brakeLights(on=False)
            self.smoke.birthRate = 0.0

    def buildCar(self, body_color=None, sound_file=None, sound_volume=1.0):
        self.chassis_node = scn.Node()
        self.chassis_node.categoryBitMask = 1 << 1

        self.body_material = scn.Material()
        self.body_material.diffuse.contents = body_color
        self.body_material.specular.contents = (0.88, 0.88, 0.88)

        self.body = scn.Box(2, 1, 4, 0.2)
        self.body.firstMaterial = self.body_material

        self.body_node = scn.Node.nodeWithGeometry(self.body)
        self.body_node.position = (0, 0.75, 0)
        self.chassis_node.addChildNode(self.body_node)

        self.physicsBody = scn.PhysicsBody.dynamicBody()
        self.physicsBody.allowsResting = False
        self.physicsBody.mass = 1200
        self.physicsBody.restitution = 0.1
        self.physicsBody.damping = 0.3
        self.chassis_node.physicsBody = self.physicsBody

        self.wheel_nodes = [scn.Node()]
        self.tire = scn.Tube(0.12, 0.35, 0.25)
        self.tire.firstMaterial.diffuse.contents = "black"
        self.wheel_nodes[0].position = (0.94, 0.4, 2 - 0.6)
        self.tire_node = scn.Node.nodeWithGeometry(self.tire)
        self.tire_node.rotation = (0, 0, 1, math.pi / 2)
        self.wheel_nodes[0].addChildNode(self.tire_node)

        self.rim = scn.Cylinder(0.14, 0.1)
        self.rim.firstMaterial.diffuse.contents = "gray"
        self.rim.firstMaterial.specular.contents = (0.88, 0.88, 0.88)
        self.rim_node = scn.Node.nodeWithGeometry(self.rim)
        self.rim_node.name = "rim"
        self.rim_node.position = (0, 0.06, 0)
        self.tire_node.addChildNode(self.rim_node)
        self.rim_deco = scn.Text("Y", 0.05)
        self.rim_deco.font = ("Arial Rounded MT Bold", 0.3)
        self.rim_deco.firstMaterial.diffuse.contents = "black"
        self.rim_deco.firstMaterial.specular.contents = (0.88, 0.88, 0.88)
        self.rim_deco_node = scn.Node.nodeWithGeometry(self.rim_deco)
        self.rim_deco_node.name = "deco"
        self.rim_deco_node.position = (-0.1, 0.03, -1.12)
        self.rim_deco_node.rotation = (1, 0, 0, math.pi / 2)
        self.rim_node.addChildNode(self.rim_deco_node)

        self.wheel_nodes.append(self.wheel_nodes[0].clone())
        self.wheel_nodes[1].position = (-0.94, 0.4, 2 - 0.6)
        self.wheel_nodes[1].childNodeWithName("rim", True).position = (0, -0.06, 0)
        self.wheel_nodes[1].childNodeWithName("deco", True).position = (
            -0.1,
            -0.03,
            -1.12,
        )
        self.wheel_nodes[1].childNodeWithName("rim", True).rotation = (
            0,
            1,
            0,
            -math.pi / 7,
        )

        self.wheel_nodes.append(self.wheel_nodes[0].clone())
        self.wheel_nodes[2].position = (0.94, 0.4, -2 + 0.7)
        self.wheel_nodes[2].childNodeWithName("rim", True).rotation = (
            0,
            1,
            0,
            math.pi / 7,
        )

        self.wheel_nodes.append(self.wheel_nodes[0].clone())
        self.wheel_nodes[3].position = (-0.94, 0.4, -2 + 0.7)
        self.wheel_nodes[3].childNodeWithName("rim", True).position = (0, -0.06, 0)
        self.wheel_nodes[3].childNodeWithName("deco", True).position = (
            -0.1,
            -0.03,
            -1.12,
        )
        self.wheel_nodes[3].childNodeWithName("rim", True).rotation = (
            0,
            1,
            0,
            math.pi / 3,
        )

        for aNode in self.wheel_nodes:
            self.chassis_node.addChildNode(aNode)

        self.wheels = [
            scn.PhysicsVehicleWheel(node=aNode) for aNode in self.wheel_nodes
        ]
        for i in [0, 1]:
            self.wheels[i].suspensionRestLength = 1.3
        for i in [2, 3]:
            self.wheels[i].suspensionRestLength = 1.4
        for aWheel in self.wheels:
            aWheel.maximumSuspensionTravel = 150

        self.chassis_node.physicsBody.contactTestBitMask = (
            scn.PhysicsCollisionCategory.Default.value
        )
        self.chassis_node.physicsBody.continuousCollisionDetectionThreshold = 2.0
        self.vehicle = scn.PhysicsVehicle(
            chassisBody=self.chassis_node.physicsBody, wheels=self.wheels
        )
        self.physics_world.addBehavior(self.vehicle)
        self.world.root_node.addChildNode(self.chassis_node)


Demo.run()
