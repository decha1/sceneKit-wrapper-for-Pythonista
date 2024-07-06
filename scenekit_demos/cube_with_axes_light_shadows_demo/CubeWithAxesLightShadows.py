# following block of code is a hack. In pythonista, user modules are reloaded automatically, i.e. there is no need to restart the interpreter. Making sceneKit a user module allows changes to take place when rerunning, as opposed to placing sceneKit in the site-packages folder, which loads only once when the interpreter starts
import sys, os.path
sceneKit_directory = os.path.dirname(__file__)
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.abspath(sceneKit_directory)
sys.path.append(sceneKit_directory)

import sceneKit as scn
import ui


def make_material(color):
    material = scn.Material()
    material.diffuse.contents = color
    return material


class axis(scn.Node):
    def __init__(self, text, color):
        super().__init__()

        self.axis = self.make_axis(color)
        self.text = self.make_text(text, color)

        self.addChildNode(self.axis)
        self.addChildNode(self.text)

    def make_axis(self, color):
        axis = scn.Node()
        axis.geometry = scn.Tube(0.05, 0.06, 20)  # Tube returns a cylinder along y axis
        axis.geometry.materials = make_material(color)
        return axis

    def make_text(self, text, color):
        string_node = scn.Node()
        string_node.geometry = scn.Text(text, 0)
        string_node.geometry.materials = make_material(color)
        string_node.scale = (0.1, 0.1, 0.1)
        string_node.position = (0, 10, 0)
        string_node.constraints = scn.BillboardConstraint.billboardConstraint()
        return string_node


class Demo:
    def __init__(self):
        self.flag = True
        self.count = 9999

    @classmethod
    def run(cls):
        cls().main()

    def main(self):
        # main view ------------------------------------------------------------------------------------
        main_view = ui.View()
        w, h = ui.get_screen_size()
        main_view.frame = (0, 0, 2, h)
        main_view.name = "Base Scene"

        # sceneView ----------------------------------------------------------------------------------------
        scene_view = scn.View(main_view.frame, superView=main_view)
        scene_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        scene_view.background_color = "black"
        scene_view.delegate = self
        scene_view.preferredFramesPerSecond = 30
        scene_view.rendersContinuously = True
        scene_view.antialiasingMode = scn.AntialiasingMode.Multisampling8X

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
        camera_node.position = (0, 0, 25)
        root_node.addChildNode(camera_node)
        scene_view.pointOfView = camera_node

        # ----------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------
        # scene objects
        #
        # axes --------------------------------------------------------------------------------------------------------------

        x_axis = axis("+x", "red")
        y_axis = axis("+y", "green")
        z_axis = axis("+z", "blue")

        x_axis.rotation = (0, 0, 1, -3.1415 / 2)
        z_axis.rotation = (1, 0, 0, 3.1415 / 2)

        root_node.addChildNode(x_axis)
        root_node.addChildNode(y_axis)
        root_node.addChildNode(z_axis)

        # box -------------
        box = scn.Node()
        box.geometry = scn.Box(10, 10, 10, 2)
        box.geometry.materials = (
            make_material("green"),
            make_material("orange"),
            make_material("blue"),
            make_material("red"),
            make_material("white"),
            make_material("yellow"),
        )
        box.geometry.chamferSegmentCount = 100
        root_node.addChildNode(box)

        # floor ------
        floor = scn.Node()
        floor.geometry = scn.Floor()
        floor.position = (0, -10, 0)
        floor.geometry.materials = make_material("grey")
        root_node.addChildNode(floor)

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
        main_light.light.intensity = 1000
        main_light.light.type = scn.LightTypeSpot
        main_light.light.castsShadow = True
        main_light.light.color = "white"
        main_light.position = (10, 10, 10)
        self.main_light = main_light

        # fill light
        fill_light = scn.Node()
        fill_light.name = "Fill Light"
        fill_light.light = scn.Light()
        fill_light.light.intensity = 400
        fill_light.light.type = scn.LightTypeDirectional
        fill_light.light.castsShadow = True
        fill_light.light.color = "white"
        fill_light.position = (-50, 200, 50)
        self.fill_light = fill_light

        # constraint ----------------------------------------------------------------------------------------
        constraint = scn.LookAtConstraint.lookAtConstraintWithTarget(root_node)
        constraint.gimbalLockEnabled = True

        camera_node.constraints = constraint
        main_light.constraints = constraint
        # fill_light.constraints = constraint

        camera_node.addChildNode(main_light)
        # camera_node.addChildNode(fill_light)
        main_view.present(style="fullscreen", hide_title_bar=False)

    def update(self, aview, atime):
        if self.flag:
            if aview.pointOfView.name == "kSCNFreeViewCameraName":
                self.flag = False
                aview.pointOfView.addChildNode(self.main_light)

        self.count += 1
        if self.count > 60:
            self.count = 0
            print(aview.pointOfView)


Demo.run()
