"""
based on the code in the thread https://forum.omz-software.com/topic/1686/3d-in-pythonista by omz
"""
# following block of code is a hack. In pythonista, user modules are reloaded automatically, i.e. there is no need to restart the interpreter. Making sceneKit a user module allows changes to take place when rerunning, as opposed to placing sceneKit in the site-packages folder, which loads only once when the interpreter starts
import sys, os.path
sceneKit_directory = os.path.dirname(__file__)
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.abspath(sceneKit_directory)
sys.path.append(sceneKit_directory)

from objc_util import *
import sceneKit as scn
import ui
import math


@on_main_thread
def demo():
    main_view = ui.View()
    w, h = ui.get_screen_size()
    main_view.frame = (0, 0, w, h)
    main_view.name = "textDemo"

    scene_view = scn.View(main_view.frame, superView=main_view)
    scene_view.autoresizingMask = (
        scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleRightMargin
    )
    scene_view.antialiasingMode = scn.AntialiasingMode.Multisampling16X

    scene_view.allowsCameraControl = True

    scene_view.backgroundColor = "white"

    scene_view.scene = scn.Scene()

    root_node = scene_view.scene.rootNode
    text_mesh = scn.Text.textWithString("Pythonista", 6.0)
    text_mesh.flatness = 0.2
    text_mesh.chamferRadius = 0.4
    text_mesh.font = ("HelveticaNeue-Bold", 18)
    bbox_min, bbox_max = text_mesh.boundingBox
    text_width = bbox_max.x - bbox_min.x
    text_node = scn.Node.nodeWithGeometry(text_mesh)
    text_node.castsShadow = True
    text_container = scn.Node.node()
    text_container.addChildNode(text_node)
    text_container.position = (0, 40, 0)
    text_node.position = (-text_width / 2, 0, 0)
    box = scn.Box(width=150, height=4, length=150, chamferRadius=1)
    box_node = scn.Node.nodeWithGeometry(box)
    root_node.addChildNode(box_node)
    rotate_action = scn.Action.repeatActionForever(
        scn.Action.rotateBy(0, math.pi * 2, math.pi * 2, 10)
    )
    text_container.runAction(rotate_action)
    root_node.addChildNode(text_container)
    light_node = scn.Node.node()
    light_node.position = (0, 105, 5)
    light_node.rotation = (1, 0, 0, -math.pi / 2)
    light = scn.Light.light()
    light.type = "spot"
    light.spotOuterAngle = 65
    light.castsShadow = True
    light.shadowSampleCount = 16
    light.shadowRadius = 10
    
    
    #light_node.scale = (7, 7, 7)
    #light.spotOuterAngle = 120
    #light.shadowRadius = 3
    light.zNear = 0
    light.zFar = 1000
    #light.shadowSampleCount = 20
    
    light.color = "cyan"
    light_node.light = light
    root_node.addChildNode(light_node)

    main_view.present(style="fullscreen", hide_title_bar=False)


demo()
