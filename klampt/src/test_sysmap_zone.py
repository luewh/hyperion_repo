from klampt import WorldModel, vis
from klampt.model.trajectory import Trajectory
from time import sleep
import math


world = WorldModel()
# res = world.loadFile("../urdf/world.xml")
res = world.loadRobot("../urdf/sysmap2.urdf")
# print(res,"\n")

vis.add("world",world)
print(vis.listItems())
vis.edit(("world","sysmap2"))

robotNum = 0
for linkIndex in range(world.numRobotLinks(robotNum)):
    world.robotLink(robotNum,linkIndex).appearance().setCreaseAngle(0)
    world.robotLink(robotNum,linkIndex).appearance().setShininess(0)
    world.robotLink(robotNum,linkIndex).appearance().setSilhouette(0)

angles = vis.getItemConfig(("world","sysmap2"))
angles[5] = -2.1
vis.setItemConfig(("world","sysmap2"),angles)
baseMax = 6.3
baseInterpol = 180
colonneMin = -0.15
colonneInterpol = 10
positions = []

for baseAngle in range(baseInterpol):
    angles[3] = baseMax * baseAngle/baseInterpol
    for colonneAngle in range(colonneInterpol):
        angles[4] = colonneMin * colonneAngle/colonneInterpol
        # print(angles)
        vis.setItemConfig(("world","sysmap2"),angles)
        positions.append(world.robot(0).link(7).getWorldPosition([0, 0, -0.17506]))
    angles[4] = 0
    # print(angles)
    vis.setItemConfig(("world","sysmap2"),angles)
    positions.append(world.robot(0).link(7).getWorldPosition([0, 0, -0.17506]))

# print(positions)
traj = Trajectory(milestones=positions)
vis.add("zone",traj)

vis.show()
while vis.shown():
    [x, y, z] = world.robot(0).link(7).getWorldPosition([0, 0, -0.17506])
    print(math.sqrt(x**2 + y**2))
    # print(vis.getItemConfig(("world","sysmap2")))
    sleep(0.1)
vis.kill()