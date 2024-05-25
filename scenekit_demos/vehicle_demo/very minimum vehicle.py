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
        self.physics_world.contactDelegate = self
        
        
        floor_geometry = scn.Floor()
        floor_geometry.reflectivity = 0.05
        tile_image = ui.Image.named("plf:Ground_DirtCenter")
        tile_number = 5
        tile_factor = scn.Matrix4(
            tile_number, 0.0, 0.0, 0.0,
            0.0, tile_number, 0.0, 0.0,
            0.0, 0.0, tile_number, 0.0,
            0.0, 0.0, 0.0, 1.0
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
        
        self.camera_node = scn.Node()
        self.camera_node.camera = scn.Camera()
        self.camera_node.camera.zFar = 150
        self.camera_node.position = scn.Vector3( 5, 10, 30)
        self.root_node.addChildNode(self.camera_node)
        
        
        
        self.car = Car(world=self.scene_view.scene)
        self.root_node.addChildNode(self.car.chassis_node)
        #self.scene_view.scene.physicsWorld.
        self.car.control()
        self.main_view.present(style="fullscreen")
        
    def update(self,a,b):
        self.car.control()
        
class Car:
    def __init__(self, world=None, props={}):
        self.world = world
        self.physics_world = world.physicsWorld
        self.buildCar()
        self.chassis_node.position = props.pop("position", (0, 0, 0))
        self.name = props.pop("name", "car")
        self.chassis_node.name = self.name
        # self.program_table = [aProg(self) for aProg in Car.programs]
        # self.current_program = CarProgram.forward
        # self.program_stack = [self.current_program]

        self.node = self.chassis_node
        self.position = self.chassis_node.position
        
        self.world.rootNode.addChildNode(self.chassis_node)
        self.physics_world.addBehavior(self.physics_vehicle)
    
    def control(self):
        self.vehicle.applyEngineForce(100, 0)
    
    def buildCar(self):
        self.chassis_node = scn.Node()

        self.car_without_wheels = self.build_car_without_wheels()
        self.chassis_node.addChildNode(self.car_without_wheels)
        
        wheel_nodes = self.build_wheels()
        for wheel_node in wheel_nodes:
            self.chassis_node.addChildNode(wheel_node)

        car_physics_body = scn.PhysicsBody.dynamicBody()
        car_physics_body.allowsResting = False
        car_physics_body.mass = 120
        car_physics_body.restitution = 0.1
        car_physics_body.damping = 0.3
        self.chassis_node.physicsBody = car_physics_body
        
        physics_wheels = [
            scn.PhysicsVehicleWheel(node=wheel_node) for wheel_node in wheel_nodes
        ]
        
 
        self.physics_vehicle = scn.PhysicsVehicle(
            chassisBody=car_physics_body, wheels=physics_wheels
        )


        print(self.chassis_node.position)
        print()
        for i in self.physics_vehicle.getWheels():
            print(i.node.position,
                  i.connectionPosition,
                  i.axle,
                  i.steeringAxis,
                  i.radius,
                  i.maximumSuspensionTravel,
                  
                  '\n',
                  sep='\n')

    def build_car_without_wheels(self):
        body_material = scn.Material()
        body_material.diffuse.contents = "#ff0000"
        body_material.specular.contents = (0.88, 0.88, 0.88)

        body = scn.Box(2, 1, 4, 0.2)
        body.firstMaterial = body_material

        body_node = scn.Node.nodeWithGeometry(body)
        body_node.position = (0, 0.75, 0)
        
        return body_node

    def build_wheels(self):

        tire = scn.Tube(0.12, 0.35, 0.25)
        tire.firstMaterial.diffuse.contents = "black"
        tire_node = scn.Node.nodeWithGeometry(tire)
        tire_node.rotation = (0, 0, 1, math.pi / 2)

        wheel_nodes = [scn.Node()]
        wheel_nodes[0].addChildNode(tire_node)


        wheel_nodes[0].position = (0.94, 0.4, 2 - 0.6)
        
        wheel_nodes.append(wheel_nodes[0].clone())
        wheel_nodes[1].position = (-0.94, 0.4, 2 - 0.6)

        wheel_nodes.append(wheel_nodes[0].clone())
        wheel_nodes[2].position = (0.94, 0.4, -2 + 0.7)
        
        wheel_nodes.append(wheel_nodes[0].clone())
        wheel_nodes[3].position = (-0.94, 0.4, -2 + 0.7)
                
        return wheel_nodes



Demo.run()
