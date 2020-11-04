import pyodrx

class ExtendedOpenDrive(pyodrx.OpenDrive):
    

    def reset(self):
        
        print(f"refreshing odr road adjustments")
        # TODO create a method to readjust in Extended Open Drive.
        for road in self.roads.values():
            road.reset()
        
        pass