import sceneKit as scn
import ui


class Demo:
    def __init__(self):
        pass

    def main(self):
        # main view ------------------------------------------------------------------------------------
        main_view = ui.View()
        w, h = ui.get_screen_size()
        main_view.frame = (0, 0, 2, h)
        main_view.name = "Base Scene"

        # sceneView ----------------------------------------------------------------------------------------
        scene_view = scn.View(main_view.frame, superVIew=main_view)
        scene_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        scene_view.background_color = "black"
        scene_view.delegate = self
        scene_view.preferredFramesPerSecond = 30
        scene_view.rendersContinuously = True

        # scene ----------------------------------------------------------------------------------------
        scene_view.scene = scn.Scene()
        root_node = scene_view.scene.rootNode

        # camera controller ----------------------------------------------------------------------------------------
        scene_view.allowsCameraControl = True
        scene_view.defaultCameraController.interactionMode = (
            scn.InteractionMode.OrbitArcball
        )

        # camera ----------------------------------------------------------------------------------------
        camera_node = scn.Node()
        camera_node.camera = scn.Camera()
        camera_node.position = (0, 30, 10)
        root_node.addChildNode(camera_node)
        scene_view.pointOfView = camera_node

        # ----------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------
        # scene objects
        #
        # axes --------------------------------------------------------------------------------------------------------------
        z_axis = scn.Node()
        z_axis.geometry = scn.Tube(0.05, 0.06, 20)
        root_node.addChildNode(z_axis)

        x_axis = scn.Node()
        x_axis.geometry = scn.Tube(0.05, 0.06, 20)
        x_axis.rotation = (0, 0, 1, 3.1415 / 2)
        root_node.addChildNode(x_axis)

        y_axis = scn.Node()
        y_axis.geometry = scn.Tube(0.05, 0.06, 20)
        y_axis.rotation = (1, 0, 0, 3.1415 / 2)
        root_node.addChildNode(y_axis)

        # ----------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------
        # lights
        #
        # ambient light ----------------------------------------------------------------------------------------------------
        ambient_light = scn.Node()
        ambient_light.light = scn.Light()
        ambient_light.light.type = scn.LightTypeAmbient
        ambient_light.light.name = "Ambient Light"
        ambient_light.light.color = "grey"
        ambient_light.light.intensity = 100
        root_node.addChildNode(ambient_light)

        # main light
        main_light = scn.Node()
        main_light.name = "Main Light"
        main_light.light = scn.Light()
        main_light.light.intensity = 400
        main_light.light.type = scn.LightTypeDirectional
        main_light.light.castsShadow = True
        main_light.light.color = "white"
        main_light.position = (50, 200, 50)

        # fill light
        fill_light = scn.Node()
        fill_light.name = "Fill Light"
        fill_light.light = scn.Light()
        fill_light.light.intensity = 400
        fill_light.light.type = scn.LightTypeDirectional
        fill_light.light.castsShadow = True
        fill_light.light.color = "white"
        fill_light.position = (-50, 200, 50)

        # constraint ----------------------------------------------------------------------------------------
        constraint = scn.LookAtConstraint.lookAtConstraintWithTarget(root_node)
        constraint.gimbalLockEnabled = True

        camera_node.constraints = constraint
        main_light.constraints = constraint
        fill_light.constraints = constraint

        main_view.present(style="fullscreen", hide_title_bar=False)

        def update(self, aview, atime):
            return
