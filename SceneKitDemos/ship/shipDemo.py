"""
modified DE
            
using the ship.scn file from XCode
"""
'''
If there is no node with a camera, a new node is created with the
name "default camera" and it's camera property set to a new camera. The pointOfView
property is set to this node. This camera is used 
to render the scene. This default node/camera seems to be created late, maybe right before
the first rendering cycle, and is the pointOfView is set to None during scene initialization.

If there are nodes with a camera, then the node with the camera that is first defined will be used as the 
the pointOfView node. The pointOfView node can also be specified by directly setting it to a node with a 
camera.


If the property allowsCameraControl is set to True, the pointOfView node remains unchanged if no 
user input occurs. After the first camera control movement occurs, a new node is created
with a new camera (I think it has the same properties as the default camera prior to user input). The original node
and original camera remain unchanged. The name of the new node is "kSCNFreeViewCameraName" and the name of the new camera
is "kSCNFreeViewCameraNameCamera". The position of the new node is transformed based on the settings of the CameraController.

The new node that is controlled by the CameraController (and by the user) does not have any child nodes. 

Nodes with lights can be added to the new camera node if you want lights to follow the camera, put code in the update
delegate

'''
from objc_util import *
import ctypes
import sceneKit as scn
import ui
import math


class Demo:
    def __init__(self):
        self.name = "ship!"
        self.count = 3000000
        self.flag = True
        
    @classmethod
    def run(cls):
        cls().main()

    #@on_main_thread
    def main(self):
        # main_view
        main_view = ui.View()
        w, h = ui.get_screen_size()
        main_view.frame = (0, 0, w, h)
        main_view.name = "ship demo"

        # scene_view
        scene_view = scn.View(main_view.frame, superView=main_view)
        scene_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        print("aaaaaa")
        print(scene_view.pointOfView)
        scene_view.scene = scn.Scene()
        scene_view.scene = scn.Scene.sceneWithURL(url="ship.scn")
        print(scene_view.pointOfView)
        
        self.scene_view = scene_view
        print(dir(scene_view.defaultCameraController))

        # shorter name for scene's rootNode
        root_node = scene_view.scene.rootNode

        # set up graphic cycle
        scene_view.delegate = self
        scene_view.preferredFramesPerSecond = 30

        # default camera setup. The default camera is a separate camera, and is
        # used by the default camera controller, which is used when we set allowsCameraControl
        # to true.
        # ??? The pointOfView property will return a node that the default camera is attached to
        # but you can't modify it?? cant attach lights?
        scene_view.allowsCameraControl = True
        scene_view.defaultCameraController.interactionMode = (
            scn.InteractionMode.OrbitArcball
        )

        # camera
        # this is a camera we define.

        camera_node = scn.Node()
        camera_node.camera = scn.Camera()
        camera_node.position = (0, 0, 5)
        root_node.addChildNode(camera_node)

        # Add a constraint to the camera to keep it pointing to the target geometry
        constraint = scn.LookAtConstraint.lookAtConstraintWithTarget(root_node)
        constraint.gimbalLockEnabled = True
        camera_node.constraints = constraint

        # get different parts of ship - left in as example code, not used
        ship_node = root_node.childNodes[0]
        ship_mesh = ship_node.childNodes[0]
        ship_emitter = ship_mesh.childNodes[0]
        ship_emitter_light = ship_emitter.light
        ship_camera = ship_mesh.camera
        scrap_meshShape = ship_mesh.geometry
        lambert1 = scrap_meshShape.materials[0]

        # light_node_1
        light_node_1 = scn.Node()
        light_node_1.position = (10, 5, 10)
        light = scn.Light()
        light.intensity = 10000
        light.type = scn.LightTypeDirectional
        light.castsShadow = True
        light.color = "blue"
        light_node_1.light = light
        light_node_1.constraints = constraint
        #scene_view.pointOfView.addChildNode(light_node_1)
        print(f"main {scene_view.pointOfView}")
        self.light_node_1 = light_node_1

        # light_node_2
        light_node_2 = scn.Node()
        light_node_2.position = (100, 50, 100)
        light = scn.Light()
        light.intensity = 1000
        light.type = scn.LightTypeDirectional
        light.castsShadow = True
        light.color = "green"
        light_node_2.light = light
        light_node_2.constraints = constraint
        root_node.addChildNode(light_node_2)

        # ambient light
        ambient_light = scn.Light()
        ambient_light.type = scn.LightTypeAmbient
        ambient_light.name = "ambient light"
        ambient_light.color = "red"
        ambient_light.intensity = 1000
        ambient_node = scn.Node()
        ambient_node.light = ambient_light
        root_node.addChildNode(ambient_node)

        main_view.present(style="fullscreen", hide_title_bar=False)

    #@on_main_thread
    def update(self, aview, atime):
        #self.light_node_1.transform = aview.pointOfView.transform
        '''
        if self.flag:
            print("flag")
            print(self.scene_view.pointOfView)
            self.scene_view.pointOfView.addChildNode(self.light_node_1)
            print(self.scene_view.pointOfView)
            self.flag = False
        return '''
        print(self.count)
        self.count += 1
        if self.count > 30:
            self.count = 0
            print("------------ update")
            print(self.scene_view.pointOfView)
            self.scene_view.pointOfView.addChildNode(self.light_node_1)
            print(self.scene_view.pointOfView)
        else:
            return
            self.scene_view.pointOfView.addChildNode(self.light_node_1)


Demo.run()
