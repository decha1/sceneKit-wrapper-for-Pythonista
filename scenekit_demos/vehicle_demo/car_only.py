import sceneKit as scn
from objc_util import *
import sceneKit as scn
import ui
import math
import random
from enum import IntEnum
import weakref
import os

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

    def buildCar(self, body_color=None, sound_file=None, sound_volume=1.0):
        self.chassis_node = scn.Node()
        self.chassis_node.categoryBitMask = 1 << 1

        self.camera_controller_node = scn.Node()

        self.camera_node = scn.Node()
        self.camera_node.position = (0, 1.6, 2.05)
        self.camera_node.lookAt((0, 0.9, 10))
        self.camera = scn.Camera()
        self.camera.zNear = 0.25
        self.camera.zFar = 10
        self.camera.fieldOfView = 35
        self.camera_node.camera = self.camera

        self.camera_controller_node.addChildNode(self.camera_node)
        self.chassis_node.addChildNode(self.camera_controller_node)

        self.radar_p1L = scn.Vector3(1.2, 1.3, 2.05)
        self.radar_p2L = scn.Vector3(4.5, 0.8, 20)
        self.radar_pSL = scn.Vector3(10.0, 0.8, 2.4)
        self.radar_p1R = scn.Vector3(-1.2, 1.3, 2.05)
        self.radar_p2R = scn.Vector3(-4.5, 0.8, 20)
        self.radar_pSR = scn.Vector3(-10.0, 0.8, 2.4)

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

        self.top = scn.Box(1.6, 0.6, 1.8, 0.1)
        self.top.firstMaterial = self.body_material
        self.top_node = scn.Node.nodeWithGeometry(self.top)
        self.top_node.position = (0, 0.5 + 0.2, 0)
        self.body_node.addChildNode(self.top_node)

        self.door1 = scn.Box(2.02, 1 - 0.2, 1.8 / 2.2, 0.08)
        self.door1.firstMaterial = self.body_material
        self.door1_node = scn.Node.nodeWithGeometry(self.door1)
        self.door1_node.position = (0, 0.1, 1.8 / 4)
        self.body_node.addChildNode(self.door1_node)

        self.door2_node = scn.Node.nodeWithGeometry(self.door1)
        self.door2_node.position = (0, 0.1, -1.8 / 4 + 0.1)
        self.body_node.addChildNode(self.door2_node)

        self.window_material = scn.Material()
        self.window_material.diffuse.contents = (0.64, 0.71, 0.75, 0.6)
        self.window_material.specular.contents = (0.88, 0.88, 0.88, 0.8)

        self.sideW1 = scn.Box(1.61, 0.6 - 0.1, 1.8 / 2.2, 0.08)
        self.sideW1.firstMaterial = self.window_material
        self.sideW1_node = scn.Node.nodeWithGeometry(self.sideW1)
        self.sideW1_node.position = (0, 0.5 + 0.2, 1.8 / 4)
        self.body_node.addChildNode(self.sideW1_node)

        self.sideW2_node = scn.Node.nodeWithGeometry(self.sideW1)
        self.sideW2_node.position = (0, 0.5 + 0.2, -1.8 / 4 + 0.1)
        self.body_node.addChildNode(self.sideW2_node)

        self.window_materials = [scn.Material() for i in range(6)]
        self.window_materials[0] = self.window_material
        self.window_materials[2] = self.window_material
        for i in [1, 3, 4, 5]:
            self.window_materials[i] = self.body_material

        alpha = math.pi / 5
        self.frontW = scn.Box(1.4, 0.6 / math.cos(alpha), 0.1, 0.06)
        self.frontW.materials = self.window_materials
        self.frontW_node = scn.Node.nodeWithGeometry(self.frontW)
        self.frontW_node.position = (
            0,
            0.5 + 0.2 - 0.05,
            1.8 / 2 + math.tan(alpha) * 0.6 / 2 - 0.1,
        )
        self.frontW_node.rotation = (1, 0, 0, -alpha)
        self.body_node.addChildNode(self.frontW_node)

        alpha = math.pi / 5
        self.frontW2 = scn.Box(1.3, 0.6 / math.cos(alpha), 0.3, 0.0)
        self.frontW2.firstMaterial = self.window_material
        self.frontW2_node = scn.Node.nodeWithGeometry(self.frontW2)
        self.frontW2_node.position = (
            0,
            0.5 + 0.2 - 0.05 - 0.2,
            1.8 / 2 + math.tan(alpha) * 0.6 / 2 - 0.08,
        )
        self.frontW2_node.rotation = (1, 0, 0, -alpha)
        self.body_node.addChildNode(self.frontW2_node)

        alpha = math.pi / 3.2
        self.rearW = scn.Box(1.4, 0.6 / math.cos(alpha), 0.2, 0.2)
        self.rearW.materials = self.window_materials
        self.rearW_node = scn.Node.nodeWithGeometry(self.rearW)
        self.rearW_node.position = (
            0,
            0.5 + 0.2 - 0.0417,
            -1.8 / 2 - math.tan(alpha) * 0.6 / 2 + 0.15,
        )
        self.rearW_node.rotation = (1, 0, 0, alpha)
        self.body_node.addChildNode(self.rearW_node)

        alpha = math.pi / 3.2
        self.rearW2 = scn.Box(1.3, 0.6 / math.cos(alpha), 0.3, 0.05)
        self.rearW2.firstMaterial = self.window_material
        self.rearW2_node = scn.Node.nodeWithGeometry(self.rearW2)
        self.rearW2_node.position = (
            0,
            0.5 + 0.2 - 0.05 - 0.2,
            -1.8 / 2 - math.tan(alpha) * 0.6 / 2 + 0.1,
        )
        self.rearW2_node.rotation = (1, 0, 0, alpha)
        self.body_node.addChildNode(self.rearW2_node)

        self.nose = scn.Pyramid(2 - 0.4, 0.15, 1 - 0.2)
        self.nose.firstMaterial = self.body_material
        self.nose_node = scn.Node.nodeWithGeometry(self.nose)
        self.nose_node.position = (0, 0.75, 2 - 0.03)
        self.nose_node.rotation = (1, 0, 0, math.pi / 2)
        self.chassis_node.addChildNode(self.nose_node)

        self.lampBack_colors = [(0.6, 0.0, 0.0), (1.0, 0.0, 0.0)]

        self.front_spot = scn.Light()
        self.front_spot.type = scn.LightTypeSpot
        self.front_spot.castsShadow = False
        self.front_spot.color = (1.0, 1.0, 0.95)
        self.front_spot.spotInnerAngle = 20
        self.front_spot.spotOuterAngle = 25
        self.front_spot.attenuationEndDistance = 15

        self.exhaust = scn.Tube(0.05, 0.07, 0.08)
        self.exhaust.firstMaterial.metalness.contents = (0.5, 0.5, 0.5)
        self.exhaust_node = scn.Node.nodeWithGeometry(self.exhaust)
        self.exhaust_node.position = (0.5, -0.42, -2.04)
        self.exhaust_node.rotation = (1, 0, 0, math.pi / 2)
        self.body_node.addChildNode(self.exhaust_node)

        self.smoke = scn.ParticleSystem()
        self.smoke.emitterShape = scn.Sphere(0.01)
        self.smoke.birthLocation = (
            scn.ParticleBirthLocation.SCNParticleBirthLocationSurface
        )
        self.smoke.birthRate = 6000
        self.smoke.loops = True
        self.smoke.emissionDuration = 0.08
        self.smoke.idleDuration = 0.4
        self.smoke.idleDurationVariation = 0.2
        self.smoke.particleLifeSpan = 0.3
        self.smoke.particleLifeSpanVariation = 1.2
        self.smoke.particleColor = (1.0, 1.0, 1.0, 1.0)
        self.smoke.particleColorVariation = (0.6, 0.0, 0.6, 0.0)
        self.smoke.blendMode = scn.ParticleBlendMode.Multiply
        self.smoke.birthDirection = scn.ParticleBirthDirection.Random
        self.smoke.particleVelocity = 2.0
        self.smoke.particleVelocityVariation = 3.5
        self.smoke.acceleration = (0.0, 15, 0.0)
        self.sizeAnim = scn.CoreBasicAnimation()
        self.sizeAnim.fromValue = 0.1
        self.sizeAnim.toValue = 0.0
        self.size_con = scn.ParticlePropertyController.controllerWithAnimation(
            self.sizeAnim
        )
        self.smoke.propertyControllers = {scn.SCNParticlePropertySize: self.size_con}

        self.smoker_node = scn.Node()
        self.smoker_node.position = (0.0, -0.15, 0.0)
        self.smoker_node.addParticleSystem(self.smoke)
        self.exhaust_node.addChildNode(self.smoker_node)

        self.lamp = scn.Tube(0.12, 0.15, 4.07)
        self.lamp.firstMaterial.metalness.contents = (0.93, 0.93, 0.93)
        self.lampGlasFront = scn.Sphere(0.13)
        self.lampGlasFront.firstMaterial.emission.contents = (0.92, 0.93, 0.66)
        self.lampGlasBack = scn.Sphere(0.13)
        self.lampGlasBack.firstMaterial.diffuse.contents = "black"
        self.lampGlasBack.firstMaterial.emission.contents = self.lampBack_colors[0]

        self.lamp_nodeR = scn.Node.nodeWithGeometry(self.lamp)
        self.lamp_nodeR.position = (-0.6, 0.75, 0.015)
        self.lamp_nodeR.rotation = (1, 0, 0, math.pi / 2)
        self.chassis_node.addChildNode(self.lamp_nodeR)
        self.lamp_nodeL = scn.Node.nodeWithGeometry(self.lamp)
        self.lamp_nodeL.position = (0.6, 0.75, 0.015)
        self.lamp_nodeL.rotation = (1, 0, 0, math.pi / 2)
        self.chassis_node.addChildNode(self.lamp_nodeL)

        self.lampGlasFront_nodeR = scn.Node.nodeWithGeometry(self.lampGlasFront)
        self.lampGlasFront_nodeR.position = (0, 1.95, 0)
        self.lampGlasFront_nodeR.lookAt((0, 45, 10))
        self.lampGlasFront_nodeR.light = self.front_spot
        self.lamp_nodeR.addChildNode(self.lampGlasFront_nodeR)
        self.lampGlasBack_nodeR = scn.Node.nodeWithGeometry(self.lampGlasBack)
        self.lampGlasBack_nodeR.position = (0, -1.95, 0)
        self.lamp_nodeR.addChildNode(self.lampGlasBack_nodeR)

        self.lampGlasFront_nodeL = scn.Node.nodeWithGeometry(self.lampGlasFront)
        self.lampGlasFront_nodeL.position = (0, 1.95, 0)
        self.lampGlasFront_nodeL.lookAt((0, 45, 10))
        self.lampGlasFront_nodeL.light = self.front_spot
        self.lamp_nodeL.addChildNode(self.lampGlasFront_nodeL)
        self.lampGlasBack_nodeL = scn.Node.nodeWithGeometry(self.lampGlasBack)
        self.lampGlasBack_nodeL.position = (0, -1.95, 0)
        self.lamp_nodeL.addChildNode(self.lampGlasBack_nodeL)

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

        if ENGINESOUND:
            self.sound = scn.AudioSource(sound_file)
            self.sound.load()
            self.sound.loops = True
            self.sound.volume = sound_volume
            self.sound_player = scn.AudioPlayer.audioPlayerWithSource(self.sound)
            self.chassis_node.addAudioPlayer(self.sound_player)

        # ---------------------------------------------------------
        # Tire tracks (i.e. the track left behind by car's wheels)
        self.tire_tracks = scn.ParticleSystem()
        self.tire_tracks.birthRate = 750
        self.tire_tracks.loops = True
        self.tire_tracks.emissionDuration = 0.1
        self.tire_tracks.particleLifeSpan = 4.6
        self.tire_tracks.particleLifeSpanVariation = 5
        self.tire_tracks.particleSize = 0.02
        self.tire_tracks.particleColor = (0.1, 0.1, 0.1, 1.0)
        self.tire_tracks.particleColorVariation = (0.1, 0.1, 0.1, 0.1)
        self.tire_tracks.blendMode = scn.ParticleBlendMode.Replace
        self.tire_tracks.emitterShape = scn.Cylinder(0.02, 0.26)
        self.tire_tracks.birthLocation = (
            scn.ParticleBirthLocation.SCNParticleBirthLocationVolume
        )
        self.tire_tracks.handle(
            scn.ParticleEvent.Birth,
            [scn.ParticlePropertyPosition],
            self.tire_tracks_particle_event_handler,
        )
        self.tire_node.addParticleSystem(self.tire_tracks)
        # ---------------------------------------------------------


Demo.run()
