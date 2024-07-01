

import sceneKit as scn


def test(node):
    return False
    
    
n = scn.Node()
n.addChildNode(scn.Node())
n.childNodesPassingTest(test)
