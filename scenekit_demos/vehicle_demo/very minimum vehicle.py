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
        self.physics_world.addBehavior(self.vehicle)
    def control(self):
        self.vehicle.applyEngineForce(100, 0)
    
    def buildCar(self):
        self.chassis_node = scn.Node()
        
        self.body_material = scn.Material()
        self.body_material.diffuse.contents = "#ff0000"
        self.body_material.specular.contents = (0.88, 0.88, 0.88)

        self.body = scn.Box(2, 1, 4, 0.2)
        self.body.firstMaterial = self.body_material

        self.body_node = scn.Node.nodeWithGeometry(self.body)
        self.body_node.position = (0, 0.75, 0)
        self.chassis_node.addChildNode(self.body_node)
        
        self.physicsBody = scn.PhysicsBody.dynamicBody()
        self.physicsBody.allowsResting = False
        self.physicsBody.mass = 120
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
        
        self.wheel_nodes.append(self.wheel_nodes[0].clone())
        self.wheel_nodes[1].position = (-0.94, 0.4, 2 - 0.6)


        self.wheel_nodes.append(self.wheel_nodes[0].clone())
        self.wheel_nodes[2].position = (0.94, 0.4, -2 + 0.7)
        

        self.wheel_nodes.append(self.wheel_nodes[0].clone())
        self.wheel_nodes[3].position = (-0.94, 0.4, -2 + 0.7)
        

        for aNode in self.wheel_nodes:
            self.chassis_node.addChildNode(aNode)

        self.physics_wheels = [
            scn.PhysicsVehicleWheel(node=aNode) for aNode in self.wheel_nodes
        ]
        
        
        
        
        
        '''
        
        for i in range(2):
            self.wheel_nodes.append(self.wheel_nodes[0].clone())
        self.wheel_nodes[1].position=(-0.94, 0.4, 2 - 0.6)
        self.wheel_nodes[1].position=(0.94, 0.4, -2 + 0.7)
        self.wheel_nodes[1].position=(-0.94, 0.4, -2 + 0.7)
        
        for aNode in self.wheel_nodes:
            self.chassis_node.addChildNode(aNode)
        self.physics_wheels = [scn.PhysicsVehicleWheel(w)  for w in self.wheel_nodes]
        '''
        self.vehicle = scn.PhysicsVehicle(
            chassisBody=self.chassis_node.physicsBody, wheels=self.physics_wheels
        )


        print(self.chassis_node.position)
        print()
        for i in self.physics_wheels:
            print(i.node.position,
                  i.connectionPosition,
                  i.axle,
                  i.steeringAxis,
                  i.radius,
                  i.maximumSuspensionTravel,
                  
                  '\n',
                  sep='\n')

Demo.run()
