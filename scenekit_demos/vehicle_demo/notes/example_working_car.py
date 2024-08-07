'''
This file is a working example of a single car of the vehicle demo.
Interesting points :
    1. the physicsBody object will not give a correct physicsShape object if the node you are working with is not part of a scene. You should add the node as a child of a scene, then assign a physicsBody to the node. If you assign a physicsBody to a node before adding the node to a scene, the physicsShape of children nodes will not be correctly placed relative to each other. If a physicsBody is assigned before adding the node to a scene, you can create a new physicsShape object and assign it to the physicsBody and this will also work.
    
    2. adding a physicsVehicle to a scene's physicsBehavior will change the wheels orientation to change relative to the car. The wheels appear to be rotated in place 180 degrees CCW along the +z axis and 90 degrees CW along the +x axis (both looking towards the origin). The rest of the vehicle does not seem to be changed.
    
    3. changing the steeringAxis or the Axis of a vehiclePhysicsWheel results in changes of position and rotation of the wheel
    
    The mechanism of how wheel position and rotation are determined once a physicsVehicle is added to a scene's physicBehavior is not clear.
'''
# following block of code is a hack. In pythonista, user modules are reloaded automatically, i.e. there is no need to restart the interpreter
import sys, os.path
sceneKit_directory = os.path.dirname(__file__)
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.abspath(sceneKit_directory)
sys.path.append(sceneKit_directory)


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

        db = [scn.DebugOption.OptionNone,
                scn.DebugOption.ShowBoundingBoxes,
                scn.DebugOption.ShowWireframe,
                scn.DebugOption.RenderAsWireframe,
                scn.DebugOption.ShowSkeletons,
                scn.DebugOption.ShowCreases,
                scn.DebugOption.ShowConstraints,
                scn.DebugOption.ShowCameras,
                scn.DebugOption.ShowLightInfluences,
                scn.DebugOption.ShowLightExtents,
                scn.DebugOption.ShowPhysicsShapes,
                scn.DebugOption.ShowPhysicsFields]
    

        self.main_view = ui.View()
        w, h = ui.get_window_size()
        self.main_view.frame = (0, 0, w, h)
        self.main_view.name = "vehicle demo"
        
        self.scene_view = scn.View((0, 0, w, h), superView=self.main_view)
        self.scene_view.preferredFramesPerSecond = 30
        self.scene_view.debugOptions = db[0]

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
        
        self.root_node.addChildNode(self.make_lights())
        
        self.car = Car(world=self.scene_view.scene)
        self.root_node.addChildNode(self.car.chassis_node)
        #self.scene_view.scene.physicsWorld.
        
        self.main_view.present(style="fullscreen")
        
    def  make_lights(self):
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
    
    def update(self,a,b):
        self.car.control()
        pass
        
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
        
        
        self.physics_world.addBehavior(self.physics_vehicle)
    
    def control(self):
        self.physics_vehicle.applyEngineForce(100, 0)
    
    def buildCar(self):
        self.chassis_node = scn.Node()
        self.world.rootNode.addChildNode(self.chassis_node)
        car_without_wheels = self.build_body_without_wheels()
        print(self.chassis_node)
        print(car_without_wheels)
        self.chassis_node.addChildNode(car_without_wheels)
        print('iiiii')
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
        
        xxx = self.physics_vehicle.getWheels()
        #xxx[0].axle = (.5,.5,.5)
        xxx[0].steeringAxis = (0,1,0)
    def build_body_without_wheels(self):
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
        
        return body_node
        

    def build_wheels(self):

        tire = scn.Tube(0.12, 0.35, 0.25)
        tire.firstMaterial.diffuse.contents = "black"
        tire_node = scn.Node.nodeWithGeometry(tire)
        tire_node.rotation = (0, 0, 1, math.pi / 2)

        rim = scn.Cylinder(0.14, 0.1)
        rim.firstMaterial.diffuse.contents = "gray"
        rim.firstMaterial.specular.contents = (0.88, 0.88, 0.88)
        rim_node = scn.Node.nodeWithGeometry(rim)
        rim_node.name = "rim"
        rim_node.position = (0, 0.06, 0)
        tire_node.addChildNode(rim_node)


        rim_deco = scn.Text("Y", 0.05)
        rim_deco.font = ("Arial Rounded MT Bold", 0.3)
        rim_deco.firstMaterial.diffuse.contents = "black"
        rim_deco.firstMaterial.specular.contents = (0.88, 0.88, 0.88)
        rim_deco_node = scn.Node.nodeWithGeometry(rim_deco)
        rim_deco_node.name = "deco"
        rim_deco_node.position = (-0.1, 0.03, -1.12)
        rim_deco_node.rotation = (1, 0, 0, math.pi / 2)
        rim_node.addChildNode(rim_deco_node)


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
