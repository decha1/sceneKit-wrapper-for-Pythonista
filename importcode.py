import sys, os.path

mango_dir = (
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) + "/another_folder/"
)

sys.path.append(mango_dir)
import mango
