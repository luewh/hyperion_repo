# from klampt import WorldModel, vis
# from time import sleep

# world = WorldModel()
# # res = world.loadFile("../urdf/world.xml")
# res = world.loadRobot("../urdf/scara.urdf")
# # print(res,"\n")

# vis.add("world",world)
# print(vis.listItems())
# vis.edit(("world","scara"))

# robotNum = 0
# for linkIndex in range(world.numRobotLinks(robotNum)):
#     world.robotLink(robotNum,linkIndex).appearance().setCreaseAngle(0)
#     world.robotLink(robotNum,linkIndex).appearance().setShininess(0)
#     world.robotLink(robotNum,linkIndex).appearance().setSilhouette(0)

# vis.show()
# while vis.shown():

#     print(vis.getItemConfig(("world","scara")))
#     sleep(0.1)
# vis.kill()