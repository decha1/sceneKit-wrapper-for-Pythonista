"""
modified DE
            
using the ship.scn file from XCode
"""
"""

When a sceneView is instantiated, the pointOfView property is set to None. 
sceneView 
    pointOfView default none
    
If pointOfView is none
    a new node is created with the name "default camera" and it's camera property set to a new camera. The pointOfView
property is set to this node. This camera is used 
to render the scene. This default node/camera seems to be created late, maybe right before
the first rendering cycle,  To get a reference
to this default camera node, read the pointOfView variable in the scene's update delegate.
Adding lights to the default camera node does not seem to affect lighting.
The position of the "default camera" node seems to depend on the objects in the scene, pointing to the center and far away enough to include all objects in the camera's field.

Attaching node with lights to the "default camera" node appears to do nothing, i.e. the light will not illuminate any
objects. Nodes with lights attached to the "kSCNFreeViewCameraName" node (see below) will work.

If a premade scene is loaded (as in the shipDemo file) a default camera appears to be already included, and can be 
referenced during initialization before rendering.

Setting the pointOfView property to a node with a camera results in the scene being rendered depending on the proprties of that camera and node.


   
If the property allowsCameraControl is set to True, the pointOfView node remains unchanged if no 
user input occurs. After the first camera control movement occurs, a new node is created
with a new camera (I think it has the same properties as the default camera prior to user input). The original node
and original camera remain unchanged. The name of the new node is "kSCNFreeViewCameraName" and the name of the new camera
is "kSCNFreeViewCameraNameCamera". The position of the new node is transformed based on the settings of the CameraController.

The new node that is controlled by the CameraController (and by the user) does not have any child nodes. 

Nodes with lights can be added to the new camera node if you want lights to follow the camera, put code in the update
delegate

"""
from objc_util import on_main_thread
import sceneKit as scn
import ui


class Demo:
    def __init__(self):
        # variables used in the update delegate
        self.count = 3000000
        self.flag = True

    @classmethod
    def run(cls):
        cls().main()

    # @on_main_thread
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
        scene_view.scene = scn.Scene()
        scene_view.scene = scn.Scene.sceneWithURL(url="ship.scn")
        scene_view.background_color = "black"
        scene_view.autoenablesDefaultLighting = True

        # shorter name for scene's rootNode
        root_node = scene_view.scene.rootNode

        # set up render cycle
        scene_view.delegate = self
        scene_view.preferredFramesPerSecond = 30
        scene_view.rendersContinuously = True
        
        # camera controller setup
        scene_view.allowsCameraControl = True
        scene_view.defaultCameraController.interactionMode = (
            scn.InteractionMode.OrbitArcball
        )

        # camera_node setup
        
        camera_node = scn.Node()
        camera_node.name = "kSCNFreeViewCameraName"
        camera_node.camera = scn.Camera()
        camera_node.camera.name = "kSCNFreeViewCameraNameCamera"
        camera_node.position = (0, 15, 15)
        root_node.addChildNode(camera_node)
        
        scene_view.pointOfView = camera_node
        
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


        # omni light
        light_1 = scn.Node()
        light_1.position = (50, 0, 0)
        light_1.constraints = constraint
        light_2 = scn.Node()
        light_2.position = (-50, 0, 0)
        light_2.constraints = constraint
        light = scn.Light()
        light.intensity = 500
        light.type = scn.LightTypeDirectional
        light.castsShadow = True
        light.color = "gray"
        light_1.light = light
        light_2.light = light
        all_lights = scn.Node()
        all_lights.addChildNode(light_1)
        all_lights.addChildNode(light_2)
        #root_node.addChildNode(omni_light)
        self.all_lights = all_lights
        camera_node.addChildNode(all_lights)
            
        # ambient light
        ambient_light = scn.Node()
        light = scn.Light()
        light.type = scn.LightTypeAmbient
        light.name = "ambient light"
        light.color = "gray"
        light.intensity = 100
        ambient_light.light = light
        root_node.addChildNode(ambient_light)

        main_view.present(style="fullscreen", hide_title_bar=False)

    # @on_main_thread
    def update(self, aview, atime):
        self.all_lights.transform = aview.pointOfView.transform
        return
        self.count += 1
        if True: #self.count > 30:
            #self.count = 0
            print("------------ update")
            print(dir(aview.defaultCameraController.getPointOfView()))
            return
            
            
            print(aview.scene.rootNode.childNodes)
            if ( (self.count % 2) == 1 ):
                self.light_node_1.light.color = "blue"
                print ("blue")
            else: 
                self.light_node_1.light.color = "red"
                print("red")
            aview.pointOfView.light = (self.light)
            return
            
            print(aview.pointOfView)
            
            print(aview.pointOfView)
        else:
            return
            aview.pointOfView.addChildNode(self.light_node_1)


Demo.run()
