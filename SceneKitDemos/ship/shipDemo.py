"""
modified DE
            
using the ship.scn file from XCode
"""

"""
Quick way to set up lights that follow camera, and have sceneKit control the camera movement
1. Create a node with its light property set to directional lights, set node constraint to "lookAtConstraintWithTarget" to point to object of interest.
2. Create a node with a camera, set node constraint to "lookAtConstraintWithTarget" to point to object of interest.
3. Set View property "allowsCameraControl" to True.
4. Add node with light as child to node with camera.

Scene will start with view rendered using the above camera.

5. Create an 'update' function and set View's delegate property to this function.
6. Inside the 'update' function. check for a new node named "kSCNFreeViewCameraName", and move the node with the directional light to this new node.

    if self.flag:
        if aview.pointOfView.name == "kSCNFreeViewCameraName":
            aview.pointOfView.addChildNode(self.directional_lights)     
            self.flag = False

The "kSCNFreeViewCameraName" node is created with the first user movement.
The light will now follow this new camera node.



1. Ambient light does not depend on position or rotation, place anywhere. Root node used in this demo.
2. Directional light does not depend on position, only rotation is important, used to mimic sunlight. Light rays are parallel with light source at infinity. Can turn on shadows.
3. Omnidirectional light mimics point source. Does not cast a shadow!!
4. Spot. Maxiumum 180 degrees light. Can turn on shadows.


"""

"""

When a sceneView is instantiated, the pointOfView property is set to None.

A. Setting pointOfView to a node
    1. setting pointOfView to a node that has no camera
        If pointOfView is set to a node whose camera property is None, then no view will be created, i.e. a blank screen will be shown. The node does not have to be part of the graph, i.e. it does not need to be a child of the scene's rootNode.
        
        If allowsCameraControl is True, the pointOfView node changes with the first user camera movement (see section D below) and the scene will be rendered based on this new node.
        
    2. setting pointOfView to a user created node with a camera.
        The view is rendered using the camera/node assigned by the user. The node does not have to be part of the graph, i.e. it does not need to be a child of the scene's rootNode.
        
        If allowsCameraControl is True, the pointOfView node changes with the first user camera movement (see section D below) and the scene will be rendered based on this new node.

B. Leaving pointOfView as None
    1. leaving pointOfView as None with no camera defined in scene
        If there is no node with a camera, the pointOfVIew property is set to a new node (created by SceneKit) with the name of "default camera", and a new camera is created and set to the camera property of this "default camera" node. This default node/camera seems to be created right before the first rendering cycle, i.e. it is not accessible during iniialization. This "default camera" node is accessible from the pointOfView property of the sceneView with code in the update delegate.
        The position of the "default camera" node appears to be adjusted so that all nodes in the scene are within the field of view.
        Attaching nodes with lights to the "default camera" node appears to do nothing, i.e. the light will not illuminate any objects.
        This "default camera" node is not part of the user graph. It does not have and parent or child nodes when created by SceneKit. Child nodes can be added, but lights do not work as described above.

        If allowsCameraControl is True, the pointOfView node changes with the first user camera movement (see section D below) and the scene will be rendered based on this new node.
        
    2. leaving pointOfView as None but nodes with cameras exist in the scene
        The pointOfView property is set to the node that has the first instantiated camera.
        
        If allowsCameraControl is True, the pointOfView node changes with the first user camera movement (see section D below) and the scene will be rendered based on this new node.
    
C. loading a scene
    In this demo, after the scene is loaded, the pointOfView propert has been set to a "default camera" node and is immediately accessible in code. It is unclear whether this "default camera" node was created after loading the scene, or if it was loaded as part of the saved scene.
    
    If allowsCameraControl is True, the pointOfView node changes with the first user camera movement (see section D below) and the scene will be rendered based on this new node.

D. allowing user to control camera 
    If the property allowsCameraControl is set to True, the pointOfView node is determined by the rules above and remains unchanged if no user input occurs. After the first camera control movement occurs, a new node is created with a new camera. The properties of this new node and camera appear to have the same properties as the original node/camera prior to the movement. The previous pointOfView node/camera remains unchanged. The name of the new node is "kSCNFreeViewCameraName" and the name of the new camera is "kSCNFreeViewCameraNameCamera". The position of the new node is transformed based on the settings of the CameraController.  
    
    The "kSCNFreeViewCameraName" node initially does not have any child or parent nodes. 

    Nodes with lights can be added to the "kSCNFreeViewCameraName" node if you want lights to follow the camera. The node with lights must be added after the creation of the "kSCNFreeViewCameraName" node, which means that the nodes must be added after the first user movement, because the "kSCNFreeViewCameraName" will not have been created before the first user movement.
    
    An easier alternative to have lights follow the camera is to set the transform property of the node containing lights equal to the transform property of the sceneView's pointOfView property in the update delegate. This has the advantage of not having to detect the creation of the "kSCNFreeViewCameraName" node with the user's first movement.
   
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
        # main_view. ------------------------------------------------------------------------
        main_view = ui.View()
        w, h = ui.get_screen_size()
        main_view.frame = (0, 0, w, h)
        main_view.name = "ship demo"

        # scene_view  ------------------------------------------------------------------------
        scene_view = scn.View(main_view.frame, superView=main_view)
        scene_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        scene_view.scene = scn.Scene()
        
        # In this specific case, the pointOfView property has beeen set to a "defaultCamera" node and is 
        # accessible immediately after loading the scene. If a scene is not loaded, the pointOfView would be None.
        scene_view.scene = scn.Scene.sceneWithURL(url="ship.scn")
        
        scene_view.background_color = "black"
        #scene_view.autoenablesDefaultLighting = True

        # shorter name for scene's rootNode
        root_node = scene_view.scene.rootNode

        # set up render cycle
        scene_view.delegate = self
        scene_view.preferredFramesPerSecond = 30
        scene_view.rendersContinuously = True

        # camera controller ------------------------------------------------------------------------
        scene_view.allowsCameraControl = True
        scene_view.defaultCameraController.interactionMode = (
            scn.InteractionMode.OrbitArcball
        )
        #scene_view.defaultCameraController.target = (0, 0, 0)
        
    
        # camera_node ------------------------------------------------------------------------
        camera_node = scn.Node()
        camera_node.camera = scn.Camera()
        
        # The camera_node can be used as the pointOfView and the scene will be rendered even if it is not added as a child of the rootNode.
        # However, the constraint lookAtConstraintWithTarget(root_node) will not work, because the camera_node is not be part
        # of the graph that has root_node
        root_node.addChildNode(camera_node)
        
        # Add a constraint to the camera to point it at a target 
        # Note that this constraint does not seem to change the transform matrix of the node
        # i.e. the rotation of the node is zero
        constraint = scn.LookAtConstraint.lookAtConstraintWithTarget(root_node)
        constraint.gimbalLockEnabled = True
        camera_node.constraints = constraint
        camera_node.position = (0, 30, 10)
        # uncomment the following line to change from the default camera (part of loading a scene)
        scene_view.pointOfView = camera_node
        self.camera_node = camera_node
        
        
        # ship parts ------------------------------------------------------------------------
        # get different parts of ship - left in as example code, not used
        ship_node = root_node.childNodes[0]
        ship_mesh = ship_node.childNodes[0]
        ship_emitter = ship_mesh.childNodes[0]
        ship_emitter_light = ship_emitter.light
        ship_camera = ship_mesh.camera
        scrap_meshShape = ship_mesh.geometry
        lambert1 = scrap_meshShape.materials[0]

        # main light ------------------------------------------------------------------------
        main_light = scn.Node()
        main_light.name = "Main Light"
        main_light.light = scn.Light()
        main_light.light.intensity = 400
        main_light.light.type = scn.LightTypeDirectional
        main_light.light.castsShadow = True
        main_light.light.color = "white"
        main_light.position = (50, 200, 50)
        main_light.constraints = constraint
        
        # fill  light ------------------------------------------------------------------------
        fill_light = scn.Node()
        fill_light.name = "Fill Light"
        fill_light.light = scn.Light()        # create a new light
        fill_light.light.intensity = 400
        fill_light.light.type = scn.LightTypeDirectional
        fill_light.light.castsShadow = True
        fill_light.light.color = "white"
        fill_light.position = (-50, 20, 50)
        fill_light.constraints = constraint

        
        self.directional_lights = scn.Node()
        self.directional_lights.constraints = constraint
        self.directional_lights.addChildNode(main_light)
        self.directional_lights.addChildNode(fill_light)

        self.camera_node.addChildNode(self.directional_lights)
        

        # ambient light -------------------------------------------------------------------------
        ambient_light = scn.Node()
        ambient_light.light = scn.Light()
        ambient_light.light.type = scn.LightTypeAmbient
        ambient_light.light.name = "ambient light"
        ambient_light.light.color = "grey"
        ambient_light.light.intensity = 100
        root_node.addChildNode(ambient_light)


        # x y z axes -------------------------------------------------------------------------
        tube_node_1 = scn.Node()
        tube_node_1.geometry = scn.Tube(0.05,0.06, 20)
        root_node.addChildNode(tube_node_1)
        tube_node_1.constraints = constraint
        root_node.addChildNode(tube_node_1)
        
        tube_node_2 = scn.Node()
        tube_node_2.geometry = scn.Tube(0.05,0.06, 20)
        tube_node_2.rotation = (0, 0, 1, 3.1415/2)
        root_node.addChildNode(tube_node_2)
        
        tube_node_3 = scn.Node()
        tube_node_3.geometry = scn.Tube(0.05,0.06, 20)
        tube_node_3.rotation = (1, 0, 0, 3.1415/2)
        root_node.addChildNode(tube_node_3)
        
        
        main_view.present(style="fullscreen", hide_title_bar=False)

    # @on_main_thread
    def update(self, aview, atime):
        #print("update")
        self.count += 1
        print(.count)
        self.camera_node.transform = aview.pointOfView.transform
        return
        
        
        if self.flag:
            if aview.pointOfView.name == "kSCNFreeViewCameraName":
                #aview.pointOfView.addChildNode(self.main_light)
                #aview.pointOfView.addChildNode(self.fill_light)
                aview.pointOfView.addChildNode(self.directional_lights)     
                self.flag = False
        
        #print(aview.pointOfView.transform)
        #self.main_light.transform = aview.pointOfView.transform   
        self.count += 1
        if self.count > 60:
            self.count = 0
            t = self.camera_node.position
            print(t.x)
            self.camera_node.position = (t.x + 5, t.y, t.z)
            #self.camera_node.position = t
            print(aview.pointOfView)
            print(self.directional_lights)
            print("-----------")
        return
        

Demo.run()
