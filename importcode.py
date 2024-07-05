# following block of code is a hack. In pythonista, user modules are reloaded automatically, i.e. there is no need to restart the interpreter. Making sceneKit a user module allows changes to take place when rerunning, as opposed to placing sceneKit in the site-packages folder, which loads only once when the interpreter starts
import sys, os.path
sceneKit_directory = os.path.dirname(__file__)
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.join(sceneKit_directory, '..')
sceneKit_directory = os.path.abspath(sceneKit_directory)
sys.path.append(sceneKit_directory)
