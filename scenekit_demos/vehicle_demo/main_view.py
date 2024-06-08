import sceneKit as scn
import ui


class MainView(ui.View):
    def __init__(self):
        super().__init__()
        w, h = ui.get_window_size()
        self.frame = (0, 0, w, h)
        self.name = "vehicle demo"

        self.scn_view = self.make_scn_view()
        self.scn_view.delegate = self

        self.scene = self.make_scene()
        self.scene.physicsWorld.contactDelegate = self
        self.scn_view.scene = self.scene

        self.camera_node = self.make_camera()
        self.scene.rootNode.addChildNode(self.camera_node)

        self.scene.rootNode.addChildNode(self.make_lights())

        self.ui_view.present(style="fullscreen", hide_title_bar=True)

    def make_scn_view(self):
        scn_view = scn.View(frame=self.bounds, superView=self)
        scn_view.preferredFramesPerSecond = 30
        scn_view.debugOptions = debug_options
        scn_view.autoresizingMask = (
            scn.ViewAutoresizing.FlexibleHeight | scn.ViewAutoresizing.FlexibleWidth
        )
        scn_view.allowsCameraControl = True
        scn_view.showsStatistics = True
        scn_view.backgroundColor = "black"
        return scn_view

    def make_scene(self):
        scene = scn.Scene()
        return scene

    def make_camera(self):
        camera_node = scn.Node()
        camera_node.camera = scn.Camera()
        camera_node.camera.zFar = 150
        camera_node.position = scn.Vector3(10, 10, 30)
        return camera_node

    def make_lights(self):
        all_lights_node = scn.Node()

        light_node = scn.Node()
        light_node.position = (50, 50, 50)
        light_node.lookAt((0, 0, 0))
        light = scn.Light()
        light.type = scn.LightTypeDirectional
        light.castsShadow = True
        light.shadowSampleCount = 16
        light.color = (0.95, 1.0, 0.98)
        light_node.light = light
        all_lights_node.addChildNode(light_node)

        ambient_node = scn.Node()
        ambient = scn.Light()
        ambient.type = scn.LightTypeAmbient
        ambient.color = (0.38, 0.42, 0.45, 0.1)
        ambient_node.light = ambient
        all_lights_node.addChildNode(ambient_node)

        return all_lights_node


if __name__ == "__main__":
    MainView()
