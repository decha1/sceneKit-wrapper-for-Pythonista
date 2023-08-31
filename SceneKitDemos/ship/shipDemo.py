"""
modified DE
            
using the ship.scn file from XCode
"""
"""

When a sceneView is instantiated, the pointOfView property is set to None. 

1. no camera defined in scene
    If there is no node with a camera, the pointOfVIew property is set to a new node (created by SceneKit) with the name of "default camera", and a new camera is created and set to the camera property of this "default camera" node. This default node/camera seems to be created right before the first rendering cycle, i.e. it is not accessible during iniialization. This "default camera" node is accessible from the pointOfView property of the sceneView with code in the update delegate.
    The position of the "default camera" node appears to be adjusted so that all nodes in the scene are within the field of view.
    Attaching nodes with lights to the "default camera" node appears to do nothing, i.e. the light will not illuminate any objects.
    This "default camera" node is not part of the user graph. It does not have and parent or child nodes when created by SceneKit. Child nodes can be added, but lights do not work as described above.

2. setting pointOfView to a user created node with a camera.
    The view is rendered using the camera/node assigned by the user. This node is unchanged by SceneKit, i.e. it is still part of the user graph, has all of the characteristics as set by the user.

3. leaving pointOfView as none but nodes with cameras exist in the scene
    The pointOfView property is set to the node that has the first instantiated camera.
    
4. allowing user to control camera 
    If the property allowsCameraControl is set to True, the pointOfView node is determined by the rules above and remains unchanged if no user input occurs. After the first camera control movement occurs, a new node is created with a new camera. The properties of this new node and camera appear to have the same properties as the original node/camera prior to the movement. The original node and original camera remain unchanged. The name of the new node is "kSCNFreeViewCameraName" and the name of the new camera is "kSCNFreeViewCameraNameCamera". The position of the new node is transformed based on the settings of the CameraController.  
    
    The "kSCNFreeViewCameraName" node does not have any child nodes. 

    Nodes with lights can be added to the "kSCNFreeViewCameraName" node if you want lights to follow the camera. The node with lights must be added after the creation of the "kSCNFreeViewCameraName" node, which means that the nodes must be added after the first user movement, because the "kSCNFreeViewCameraName" will not have been created before the first user movement.
    
    An easier alternative to have lights follow the camera is to set the transform property of the node containing lights equal to the transform property of the sceneView's pointOfView property in the update delegate. This has the advantage of not having to detect the creation of the "kSCNFreeViewCameraName" node with the user's first movement.



If a premade scene is loaded (as in the shipDemo file) the pointOfView may already be set to a node with a camera. This node may be accessed from code before the first render cycle.
   

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
        camera_node.camera = scn.Camera()
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

        # directional light
        directional_light = scn.Light()
        directional_light.intensity = 500
        directional_light.type = scn.LightTypeDirectional
        directional_light.castsShadow = True
        directional_light.color = "gray"

        light_1 = scn.Node()
        light_1.position = (50, 0, 0)
        light_1.constraints = constraint
        light_1.light = directional_light

        light_2 = scn.Node()
        light_2.position = (-50, 0, 0)
        light_2.constraints = constraint
        light_2.light = directional_light

        all_directional_lights = scn.Node()
        all_directional_lights.addChildNode(light_1)
        all_directional_lights.addChildNode(light_2)
        all_directional_lights.transform = scene_view.pointOfView.transform
        root_node.addChildNode(all_directional_lights)
        self.all_directional_lights = all_directional_lights

        # ambient light
        ambient_light = scn.Light()
        ambient_light.type = scn.LightTypeAmbient
        ambient_light.name = "ambient light"
        ambient_light.color = "gray"
        ambient_light.intensity = 100

        ambient_node = scn.Node()
        ambient_node.light = ambient_light
        root_node.addChildNode(ambient_node)

        main_view.present(style="fullscreen", hide_title_bar=False)

    # @on_main_thread
    def update(self, aview, atime):
        self.all_directional_lights.transform = aview.pointOfView.transform
        return
        self.count += 1
        if True:  # self.count > 30:
            # self.count = 0
            print("------------ update")
            print(dir(aview.defaultCameraController.getPointOfView()))
            return

            print(aview.scene.rootNode.childNodes)
            if (self.count % 2) == 1:
                self.light_node_1.light.color = "blue"
                print("blue")
            else:
                self.light_node_1.light.color = "red"
                print("red")
            aview.pointOfView.light = self.light
            return

            print(aview.pointOfView)

            print(aview.pointOfView)
        else:
            return
            aview.pointOfView.addChildNode(self.light_node_1)


Demo.run()
