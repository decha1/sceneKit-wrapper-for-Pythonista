"""
using the Corvette-F3.scn file
"""
# following block of code is a hack. In pythonista, user modules are reloaded automatically, i.e. there is no need to restart the interpreter. Making sceneKit a user module allows changes to take place when rerunning, as opposed to placing sceneKit in the site-packages folder, which loads only once when the interpreter starts
import sys, os.path
sceneKit_directory = os.path.dirname(__file__)
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.abspath(sceneKit_directory)
sys.path.append(sceneKit_directory)

from objc_util import *
import ctypes
import sceneKit as scn
import ui
import math


class Demo:
    def __init__(self):
        self.name = "Corvette-F3"
        pass

    @classmethod
    def run(cls):
        cls().main()

    @on_main_thread
    def main(self):
        main_view = ui.View()
        w, h = ui.get_screen_size()
        main_view.frame = (0, 0, w, h)
        main_view.name = "Corvette-F3 demo"

        scene_view = scn.View(main_view.frame, superView=main_view)
        scene_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        scene_view.allowsCameraControl = True

        scene_view.scene = scn.Scene.sceneWithURL(url="Corvette-F3.scn")

        root_node = scene_view.scene.rootNode
        corvette_node = root_node.childNodes[0]

        corvette_geometry = corvette_node.geometry
        corvette_material = corvette_geometry.firstMaterial

        corvette_material.diffuse.contents = ui.Image.named(
            "SF_Corvette-F3_diffuse.jpg"
        )
        corvette_material.emission.contents = ui.Image.named("SF_Corvette-F3_glow.jpg")
        corvette_material.specular.contents = ui.Image.named(
            "SF_Corvette-F3_specular.jpg"
        )
        corvette_material.normal.contents = ui.Image.named("SF_Corvette-F3_bump.jpg")

        constraint = scn.LookAtConstraint.lookAtConstraintWithTarget(corvette_node)
        constraint.gimbalLockEnabled = True

        light_node = scn.Node()
        light_node.position = (-800, -800, -2100)
        light = scn.Light()
        light.type = scn.LightTypeDirectional
        light.castsShadow = True
        light.color = (0.89, 0.89, 0.89)
        light.intensity = 500
        light_node.light = light
        light_node.constraints = constraint
        root_node.addChildNode(light_node)

        ambient_light = scn.Light()
        ambient_light.type = scn.LightTypeAmbient
        ambient_light.name = "ambient light"
        ambient_light.color = (0.99, 1.0, 0.86)
        ambient_light.intensity = 300
        ambient_node = scn.Node()
        ambient_node.light = ambient_light
        root_node.addChildNode(ambient_node)

        main_view.present(style="fullscreen", hide_title_bar=False)


Demo.run()
