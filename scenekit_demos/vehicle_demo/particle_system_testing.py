from main_view import MainView
import sceneKit as scn


def _add_exhaust_smoke_particle_system(self):
    # add exhaust smoke
    smoke = scn.ParticleSystem()
    smoke.emitterShape = scn.Sphere(0.01)
    smoke.birthLocation = scn.ParticleBirthLocation.SCNParticleBirthLocationSurface
    smoke.birthRate = 6000
    smoke.loops = True
    smoke.emissionDuration = 0.08
    smoke.idleDuration = 0.4
    smoke.idleDurationVariation = 0.2
    smoke.particleLifeSpan = 0.3
    smoke.particleLifeSpanVariation = 1.2
    smoke.particleColor = (1.0, 1.0, 1.0, 1.0)
    smoke.particleColorVariation = (0.6, 0.0, 0.6, 0.0)
    smoke.blendMode = scn.ParticleBlendMode.Multiply
    smoke.birthDirection = scn.ParticleBirthDirection.Random
    smoke.particleVelocity = 2.0
    smoke.particleVelocityVariation = 3.5
    smoke.acceleration = (0.0, 15, 0.0)
    sizeAnim = scn.CoreBasicAnimation()
    sizeAnim.fromValue = 0.1
    sizeAnim.toValue = 0.0
    size_con = scn.ParticlePropertyController.controllerWithAnimation(sizeAnim)
    smoke.propertyControllers = {scn.SCNParticlePropertySize: size_con}

    smoker_node = scn.Node()
    smoker_node.position = (0.0, -0.15, 0.0)
    smoker_node.addParticleSystem(smoke)
    exhaust_node = self.childNodeWithName("exhaust", True)
    exhaust_node.addChildNode(smoker_node)

    self.smoke = smoke


view = MainView()
view.scene.rootNode.addChildNode(_add_exhaust_smoke_particle_system())
