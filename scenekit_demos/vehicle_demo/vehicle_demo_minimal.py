"""
minimal test scene
"""

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


def distance(aNode, bNode):
    a = aNode.position
    b = bNode.position
    return dist(a, b)


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(list(a), list(b))))


def length(a):
    return math.sqrt(sum(x**2 for x in a))


def dot(v1, v2):
    return sum(x * y for x, y in zip(list(v1), list(v2)))


def det2(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]


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
        cars_properties = [
            dict(name="red", position=(5, 0, 0), volume=1.0),
            dict(
                name="yellow",
                too_far=25,
                body_color=(1.0, 0.78, 0.0),
                position=(-5, 0, -2),
                sound="game:Pulley",
                volume=0.1,
            ),
            dict(
                name="blue",
                too_far=30,
                body_color=(0.0, 0.61, 1.0),
                position=(-12, 0, -6),
                sound="game:Woosh_1",
                volume=0.5,
            ),
            dict(
                name="green",
                too_far=18,
                body_color=(0.0, 0.82, 0.28),
                position=(10, 0, -10),
                sound="casino:DiceThrow3",
                volume=0.8,
            ),
            dict(
                name="pink",
                too_far=20,
                body_color=(0.91, 0.52, 0.62),
                position=(5, 0, 10),
                sound="casino:DieThrow3",
                volume=0.5,
            ),
        ]
        self.cars = [
            Car(world=self, props=cars_properties[i]) for i in range(len(cars))
        ]
        # ---------------------------------------------------------------------------

        # ---------------------------------------------------------------------------
        # Flags
        self.free_flags = []
        for i in range(2 * len(self.cars)):
            node = scn.Node()
            self.free_flags.append(node)
            self.root_node.addChildNode(node)
        self.used_flags = {}
        # ---------------------------------------------------------------------------

        # ---------------------------------------------------------------------------
        # Sparks
        self.crash = Sparks().particleSystem
        self.crash_sound = scn.AudioSource("game:Crashing")
        self.crash_action = scn.Action.playAudioSource(self.crash_sound, False)
        # ---------------------------------------------------------------------------

        # ---------------------------------------------------------------------------
        # roadblocks
        self.road_blocks_node = scn.Node()
        self.road_blocks = []

        self.road_blocks.append(
            RoadBlock(w=1.6, l=25, name="block 0", position=(28, 6))
        )
        self.road_blocks.append(
            RoadBlock(w=20, l=1.6, name="block 1", position=(-2, -12))
        )
        self.road_blocks.append(
            RoadBlock(
                w=8, l=1.6, name="block 2", position=(-10, 6), rotation=-math.pi / 6
            )
        )
        self.road_blocks.append(
            RoadBlock(
                w=40,
                l=1.6,
                name="block 3",
                position=(-40, 0),
                rotation=-math.pi / 3,
            )
        )
        self.road_blocks.append(
            RoadBlock(w=0.8, h=3, l=0.8, name="start", position=(0, 0))
        )

        for aBlock in self.road_blocks:
            self.road_blocks_node.addChildNode(aBlock.block_node)

        self.root_node.addChildNode(self.road_blocks_node)
        # ---------------------------------------------------------------------------

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

        self.is_close_clicked = False
        self.is_shutting_down = False
        self.main_view.add_subview(self.close_button)
        self.main_view.present(style="fullscreen", hide_title_bar=(not DEBUG))

    def close(self, sender):
        self.is_close_clicked = True
        self.main_view.remove_subview(self.close_button)

    def shut_down(self):
        self.is_shutting_down = True
        self.crash = None
        print("before close")
        self.main_view.close()

    def update(self, view, atTime):
        print("update")
        if self.is_close_clicked:
            if not self.is_shutting_down:
                self.shut_down()
        return


class Car:
    def __init__(self, world=None, properties={}):
        return


class Sparks:
    def __init__(self):
        self.flag = scn.Sphere(0.05)
        self.particleSystem = scn.ParticleSystem()
        self.particleSystem.loops = True
        self.particleSystem.birthRate = 550
        self.particleSystem.emissionDuration = 2
        self.particleSystem.particleLifeSpan = 0.18
        self.particleSystem.particleLifeSpanVariation = 0.29
        self.particleSystem.particleVelocity = 8
        self.particleSystem.particleVelocityVariation = 15
        self.particleSystem.particleSize = 0.04
        self.particleSystem.particleSizeVariation = 0.03
        self.particleSystem.stretchFactor = 0.02
        self.particleSystemColorAnim = scn.CoreKeyframeAnimation()
        self.particleSystemColorAnim.values = [
            (0.99, 1.0, 0.71, 0.8),
            (1.0, 0.52, 0.0, 0.8),
            (1.0, 0.0, 0.1, 1.0),
            (0.78, 0.0, 0.0, 0.3),
        ]
        self.particleSystemColorAnim.keyTimes = (0.0, 0.1, 0.8, 1.0)
        self.particleSystemProp_con = (
            scn.ParticlePropertyController.controllerWithAnimation(
                self.particleSystemColorAnim
            )
        )
        self.particleSystem.propertyControllers = {
            scn.SCNParticlePropertyColor: self.particleSystemProp_con
        }
        self.particleSystem.emitterShape = self.flag
        self.particleSystem.birthLocation = (
            scn.ParticleBirthLocation.SCNParticleBirthLocationSurface
        )
        self.particleSystem.birthDirection = scn.ParticleBirthDirection.Random


class RoadBlock:
    block_material = scn.Material()
    block_material.diffuse.contents = (0.91, 0.91, 0.91)
    block_material.specular.contents = (0.88, 0.88, 0.88)

    def __init__(
        self, w=1.0, h=1.8, l=2.0, name="block", position=(0.0, 0.0), rotation=0.0
    ):
        self.block = scn.Box(w, h, l, 0.1)
        self.block.firstMaterial = RoadBlock.block_material
        self.block_node = scn.Node.nodeWithGeometry(self.block)
        self.block_node.name = name
        self.block_node.position = (
            position if len(position) == 3 else (position[0], h / 2 - 0.2, position[1])
        )
        self.block_node.rotation = (0, 1, 0, rotation)
        self.block_node.physicsBody = scn.PhysicsBody.staticBody()
        self.block_node.physicsBody.contactTestBitMask = (
            scn.PhysicsCollisionCategory.Default.value
        )


Demo.run()
