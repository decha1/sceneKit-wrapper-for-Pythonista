# following block of code is a hack. In pythonista, user modules are reloaded automatically, i.e. there is no need to restart the interpreter
import sys, os.path
sceneKit_directory = os.path.dirname(__file__)
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.abspath(sceneKit_directory)
sys.path.append(sceneKit_directory)

from main_view import MainView
from objc_util import *
import sceneKit as scn
import ctypes

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename="debug.log", encoding="utf-8", level=logging.DEBUG)

block_code = None

def handleEvent(particle_system, event, properties, block):
    
    ## for this to work you have to set the corresponding property variation value to anything but the default! Apple bug:
    ## done via self.blockEnabler(aProperty)
    
    blockInstance = ParticleEventBlock(event, properties, block)
    self.particleEventBlocks.append(blockInstance)
    
    #print (event,properties,blockInstance, blockInstance.blockCode)
    #return
    self.ID.handleEvent_forProperties_withBlock_(
        event.value, properties, blockInstance.blockCode
    )
        
class ParticleEventBlock:
    ## for this to work you have to set the corresponding property variation value to anything but the default! Apple bug:
    ## done via self.blockEnabler(aProperty)
    def __init__(self, event, properties, block):
        self.blockCode = ObjCBlock(
            self.blockInterface,
            restype=None,
            argtypes=[
                c_void_p,
                POINTER(c_void_p),
                POINTER(c_size_t),
                POINTER(c_uint32),
                NSInteger,
            ],
        )
        self.event = event
        if event == ParticleEvent.Birth:
            self.pInd = lambda ind, partInd: partInd
        else:
            self.pInd = lambda ind, partInd: ind[partInd]
        self.properties = properties
        self.propertyNumber = len(properties)
        self.pCode = block

def blockInterface(self, _cmd, xData, dataStride, indicies, count):
    print('scn bloc')
    print (self, _cmd, xData, dataStride, indicies, count)
    self.pCode(_cmd, xData, dataStride, indicies, count)
    return
    for particleIndex in range(count):
        pInd = self.pInd(indicies, particleIndex)
        for aPropertyIndex in range(self.propertyNumber):
            offset = dataStride[aPropertyIndex] * pInd
            propAddr = xData[aPropertyIndex] + offset
            prop = cast(propAddr, POINTER(c_float))
            self.pCode(prop, self.properties[aPropertyIndex], particleIndex)



def particle_system_handler():
    #logger.debug('inside handler')
    #print("handler")
    return 


def _add_exhaust_smoke_particle_system(x=None):
    # add exhaust smoke
    smoke = scn.ParticleSystem()
    
    smoke.emitterShape = scn.Sphere(0.01)
    
    smoke.birthLocation = scn.ParticleBirthLocation.SCNParticleBirthLocationSurface
    smoke.birthRate = 100
    
    smoke.loops = True
    smoke.emissionDuration = 1#0.08
    smoke.idleDuration = 1#0.4
    smoke.idleDurationVariation = 0#0.2
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
    ''' '''
    smoker_node = scn.Node()
    smoker_node.position = (0.0, 1, 0.0)
    smoker_node.addParticleSystem(smoke)

    smoke.handleEvent(scn.ParticleEvent.Birth,
            [scn.ParticlePropertyPosition],
            particle_system_handler)
            
    if x:
        global block_code
        block_code = ObjCBlock(
            particle_system_handler,
            restype=None,
            argtypes=[
                c_void_p,
                POINTER(c_void_p),
                POINTER(ctypes.c_size_t),
                POINTER(ctypes.c_uint32),
                NSInteger
            ]
        )
        print(block_code)
        smoke.ID.handleEvent_forProperties_withBlock_(scn.ParticleEvent.Birth, [scn.ParticlePropertyPosition], block_code)
        self.tire_tracks.handle(
            scn.ParticleEvent.Birth,
            [scn.ParticlePropertyPosition],
            self.trackParticleEventBlock,
        )
        #smoke.ID.handleEvent_forProperties_withBlock_(0, [], None)
        logger.debug('after setting handleEvent')
    return smoker_node

    
logger.debug('starting')
view = MainView()

view.scene.rootNode.addChildNode(_add_exhaust_smoke_particle_system(False))

view.present(style="fullscreen", hide_title_bar=True)
