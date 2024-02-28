#!/usr/bin/env python3

#Interafce Tkinker avec des voyants, boutons labels et autres
#les entrées des voyants proviennent de topic ROS

import time
import platform

from InterfaceIHM import IHM
from Subscriber import Subscriber

if __name__ == "__main__":
    
    IHM = IHM()
    
    if platform.system() != "Windows":
        Subscriber= Subscriber(IHM)
    
    # IHM.mainloop()
