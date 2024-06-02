import sceneKit as scn
import math

class Car(scn.Node):
    def control(self):
        self.physics_vehicle.applyEngineForce(1000, 0)
        self.physics_vehicle.applyEngineForce(1000, 1)

    def __init__(self, scene, properties, simple=False):
        super().__init__()
        temp_node = scn.Node()
        self.position = (0, 3, 0)

        if simple:
            body = self.simple_make_body_without_wheels()
            wheels = self.simple_make_wheels()
        else:
            body = self.make_body_without_wheels()
            wheels = self.make_wheels()

        self.addChildNode(body)
        
        
        scene.rootNode.addChildNode(self)
        
        physicsBody = scn.PhysicsBody.dynamicBody()
        physicsBody.allowsResting = False
        physicsBody.mass = 1200
        physicsBody.restitution = 0.1
        physicsBody.damping = 0.3
        
        self.physicsBody = physicsBody
        #self.physicsBody.physicsShape = scn.PhysicsShape(node=self)
        
        for wheel in wheels:
            self.addChildNode(wheel)
            
        physics_wheels = map(scn.PhysicsVehicleWheel, wheels)
        self.physics_vehicle = scn.PhysicsVehicle(
            chassisBody=physicsBody, wheels=physics_wheels
        )
        scene.physicsWorld.addBehavior(self.physics_vehicle)
        
        
    def simple_make_body_without_wheels(self):
        body = self.make_box(1)
        body.position=(0,0.75,0)
        a = self.make_box(2)
        a.position=(0,0,0)
        #body.addChildNode(a)
        return body
        
    def simple_make_wheels(self):
        #wheel = self.make_box(1)
        base_wheel = self.make_tube(0.3, 0.5, 0.2)
        
        # rotate whee for right sided wheels
        base_wheel.rotation = (0,0,1, -math.pi/2)
        
        
        fr_wheel = scn.Node()
        fr_wheel.addChildNode(base_wheel.clone())
        fr_wheel.position = (-1, 0, 1)
        
        br_wheel = scn.Node()
        br_wheel.addChildNode(base_wheel.clone())
        br_wheel.position = (-1, 0, -1)
        
        #rotate wheel for left sided wheels
        base_wheel.rotation = (0,0,1, math.pi/2)
        fl_wheel = scn.Node()
        fl_wheel.addChildNode(base_wheel.clone())
        fl_wheel.position = (1, 0, 1)
        
        bl_wheel = scn.Node()
        bl_wheel.addChildNode(base_wheel.clone())
        bl_wheel.position = (1, 0, -1)
        
        wheels = [fr_wheel, br_wheel, fl_wheel, bl_wheel]
        return wheels

    def make_tube(self, inner, outer, thickness):
        geometry = scn.Tube(inner, outer, thickness)
        #lg = scn.Material()
        #lg.diffuse.contents = "lightgrey"
        #geometry.materials = [lg]
        
        return scn.Node.nodeWithGeometry(geometry)
        
    def make_box(self, size):
        geometry = scn.Box(size, size, size)
        r = scn.Material()
        r.diffuse.contents = "red"
        b = scn.Material()
        b.diffuse.contents = "blue"
        g = scn.Material()
        g.diffuse.contents = "green"
        lg = scn.Material()
        lg.diffuse.contents = "lightgrey"

        geometry.materials = [b, r, lg, lg, g, lg]

        return scn.Node.nodeWithGeometry(geometry)

    def make_body_without_wheels(self):

        body_material = scn.Material()
        body_material.diffuse.contents = "#ff0000"
        body_material.specular.contents = (0.88, 0.88, 0.88)

        body = scn.Box(2, 1, 4, 0.2)
        body.firstMaterial = body_material

        body_node = scn.Node.nodeWithGeometry(body)
        body_node.position = (0, 0.75, 0)
        
        top = scn.Box(1.6, 0.6, 1.8, 0.1)
        top.firstMaterial = body_material
        top_node = scn.Node.nodeWithGeometry(top)
        top_node.position = (0, 0.5 + 0.2, 0)
        body_node.addChildNode(top_node)
        
        
        door1 = scn.Box(2.02, 1 - 0.2, 1.8 / 2.2, 0.08)
        door1.firstMaterial = body_material
        door1_node = scn.Node.nodeWithGeometry(door1)
        door1_node.position = (0, 0.1, 1.8 / 4)
        body_node.addChildNode(door1_node)

        door2_node = scn.Node.nodeWithGeometry(door1)
        door2_node.position = (0, 0.1, -1.8 / 4 + 0.1)
        body_node.addChildNode(door2_node)
        
        window_material = scn.Material()
        window_material.diffuse.contents = (0.64, 0.71, 0.75, 0.6)
        window_material.specular.contents = (0.88, 0.88, 0.88, 0.8)

        sideW1 = scn.Box(1.61, 0.6 - 0.1, 1.8 / 2.2, 0.08)
        sideW1.firstMaterial = window_material
        sideW1_node = scn.Node.nodeWithGeometry(sideW1)
        sideW1_node.position = (0, 0.5 + 0.2, 1.8 / 4)
        body_node.addChildNode(sideW1_node)

        sideW2_node = scn.Node.nodeWithGeometry(sideW1)
        sideW2_node.position = (0, 0.5 + 0.2, -1.8 / 4 + 0.1)
        body_node.addChildNode(sideW2_node)

        window_materials = [scn.Material() for i in range(6)]
        window_materials[0] = window_material
        window_materials[2] = window_material
        for i in [1, 3, 4, 5]:
            window_materials[i] = body_material

        alpha = math.pi / 5
        frontW = scn.Box(1.4, 0.6 / math.cos(alpha), 0.1, 0.06)
        frontW.materials = window_materials
        frontW_node = scn.Node.nodeWithGeometry(frontW)
        frontW_node.position = (
            0,
            0.5 + 0.2 - 0.05,
            1.8 / 2 + math.tan(alpha) * 0.6 / 2 - 0.1,
        )
        frontW_node.rotation = (1, 0, 0, -alpha)
        body_node.addChildNode(frontW_node)

        alpha = math.pi / 5
        frontW2 = scn.Box(1.3, 0.6 / math.cos(alpha), 0.3, 0.0)
        frontW2.firstMaterial = window_material
        frontW2_node = scn.Node.nodeWithGeometry(frontW2)
        frontW2_node.position = (
            0,
            0.5 + 0.2 - 0.05 - 0.2,
            1.8 / 2 + math.tan(alpha) * 0.6 / 2 - 0.08,
        )
        frontW2_node.rotation = (1, 0, 0, -alpha)
        body_node.addChildNode(frontW2_node)

        alpha = math.pi / 3.2
        rearW = scn.Box(1.4, 0.6 / math.cos(alpha), 0.2, 0.2)
        rearW.materials = window_materials
        rearW_node = scn.Node.nodeWithGeometry(rearW)
        rearW_node.position = (
            0,
            0.5 + 0.2 - 0.0417,
            -1.8 / 2 - math.tan(alpha) * 0.6 / 2 + 0.15,
        )
        rearW_node.rotation = (1, 0, 0, alpha)
        body_node.addChildNode(rearW_node)

        alpha = math.pi / 3.2
        rearW2 = scn.Box(1.3, 0.6 / math.cos(alpha), 0.3, 0.05)
        rearW2.firstMaterial = window_material
        rearW2_node = scn.Node.nodeWithGeometry(rearW2)
        rearW2_node.position = (
            0,
            0.5 + 0.2 - 0.05 - 0.2,
            -1.8 / 2 - math.tan(alpha) * 0.6 / 2 + 0.1,
        )
        rearW2_node.rotation = (1, 0, 0, alpha)
        body_node.addChildNode(rearW2_node)

        nose = scn.Pyramid(2 - 0.4, 0.15, 1 - 0.2)
        nose.firstMaterial = body_material
        nose_node = scn.Node.nodeWithGeometry(nose)
        nose_node.position = (0, 0, 2 - 0.03)
        nose_node.rotation = (1, 0, 0, math.pi / 2)
        body_node.addChildNode(nose_node)

        lampBack_colors = [(0.6, 0.0, 0.0), (1.0, 0.0, 0.0)]

        front_spot = scn.Light()
        front_spot.type = scn.LightTypeSpot
        front_spot.castsShadow = False
        front_spot.color = (1.0, 1.0, 0.95)
        front_spot.spotInnerAngle = 20
        front_spot.spotOuterAngle = 25
        front_spot.attenuationEndDistance = 15

        exhaust = scn.Tube(0.05, 0.07, 0.08)
        exhaust.firstMaterial.metalness.contents = (0.5, 0.5, 0.5)
        exhaust_node = scn.Node.nodeWithGeometry(exhaust)
        exhaust_node.position = (0.5, -0.42, -2.04)
        exhaust_node.rotation = (1, 0, 0, math.pi / 2)
        body_node.addChildNode(exhaust_node)

        lamp = scn.Tube(0.12, 0.15, 4.07)
        lamp.firstMaterial.metalness.contents = (0.93, 0.93, 0.93)
        lampGlasFront = scn.Sphere(0.13)
        lampGlasFront.firstMaterial.emission.contents = (0.92, 0.93, 0.66)
        lampGlasBack = scn.Sphere(0.13)
        lampGlasBack.firstMaterial.diffuse.contents = "black"
        lampGlasBack.firstMaterial.emission.contents = lampBack_colors[0]

        lamp_nodeR = scn.Node.nodeWithGeometry(lamp)
        lamp_nodeR.position = (-0.6, 0, 0.015)
        lamp_nodeR.rotation = (1, 0, 0, math.pi / 2)
        body_node.addChildNode(lamp_nodeR)
        lamp_nodeL = scn.Node.nodeWithGeometry(lamp)
        lamp_nodeL.position = (0.6, 0, 0.015)
        lamp_nodeL.rotation = (1, 0, 0, math.pi / 2)
        body_node.addChildNode(lamp_nodeL)

        lampGlasFront_nodeR = scn.Node.nodeWithGeometry(lampGlasFront)
        lampGlasFront_nodeR.position = (0, 1.95, 0)
        lampGlasFront_nodeR.lookAt((0, 45, 10))
        lampGlasFront_nodeR.light = front_spot
        lamp_nodeR.addChildNode(lampGlasFront_nodeR)
        lampGlasBack_nodeR = scn.Node.nodeWithGeometry(lampGlasBack)
        lampGlasBack_nodeR.position = (0, -1.95, 0)
        lamp_nodeR.addChildNode(lampGlasBack_nodeR)

        lampGlasFront_nodeL = scn.Node.nodeWithGeometry(lampGlasFront)
        lampGlasFront_nodeL.position = (0, 1.95, 0)
        lampGlasFront_nodeL.lookAt((0, 45, 10))
        lampGlasFront_nodeL.light = front_spot
        lamp_nodeL.addChildNode(lampGlasFront_nodeL)
        lampGlasBack_nodeL = scn.Node.nodeWithGeometry(lampGlasBack)
        lampGlasBack_nodeL.position = (0, -1.95, 0)
        lamp_nodeL.addChildNode(lampGlasBack_nodeL)

        return body_node

    def make_wheels(self):
        #return []
        tire = scn.Tube(0.12, 0.35, 0.25)
        tire.firstMaterial.diffuse.contents = "black"
        tire_node = scn.Node.nodeWithGeometry(tire)

        rim = scn.Cylinder(0.14, 0.1)
        rim.firstMaterial.diffuse.contents = "gray"
        rim.firstMaterial.specular.contents = (0.88, 0.88, 0.88)
        rim_node = scn.Node.nodeWithGeometry(rim)
        rim_node.name = "rim"
        rim_node.position = (0, 0.06, 0)

        rim_deco = scn.Text("Y", 0.05)
        rim_deco.font = ("Arial Rounded MT Bold", 0.3)
        rim_deco.firstMaterial.diffuse.contents = "black"
        rim_deco.firstMaterial.specular.contents = (0.88, 0.88, 0.88)
        rim_deco_node = scn.Node.nodeWithGeometry(rim_deco)
        rim_deco_node.name = "deco"
        rim_deco_node.position = (-0.1, 0.03, -1.12)
        rim_deco_node.rotation = (1, 0, 0, math.pi / 2)
        rim_node.addChildNode(rim_deco_node)

        # base wheel is tire+rim+rim deco lying flat, deco facing up
        base_wheel_node = scn.Node()
        base_wheel_node.addChildNode(tire_node)
        base_wheel_node.addChildNode(rim_node)
        base_wheel_node.addChildNode(rim_deco_node)
        base_wheel_node.name = "base-wheel"
        
        #rotate base for left-sided wheels
        base_wheel_node.rotation = (0, 0, 1, -math.pi/2)
        
        fl_wheel = scn.Node()
        fl_wheel.name = "front-left wheel"
        fl_wheel.addChildNode(base_wheel_node.clone())
        fl_wheel.position = (0.94, 0.4, 2 - 0.6)
        
        bl_wheel = scn.Node()
        bl_wheel.name = "back-left wheel"
        bl_wheel.addChildNode(base_wheel_node.clone())
        bl_wheel.position = (0.94, 0.4, -2 + 0.7)

        #rotate base for right-sided wheels
        base_wheel_node.rotation = (0, 0, 1, math.pi/2)
        
        fr_wheel = scn.Node()
        fr_wheel.name = "front-right wheel"
        fr_wheel.addChildNode(base_wheel_node.clone())
        fr_wheel.position = (-0.94, 0.4, 2 - 0.6)
        
        br_wheel = scn.Node()
        br_wheel.name = "back-right wheel"
        br_wheel.addChildNode(base_wheel_node.clone())
        br_wheel.position = (-0.94, 0.4, -2 + 0.7)
        
        
        


        return [br_wheel, bl_wheel, fr_wheel, fl_wheel]  # wheel_nodes
