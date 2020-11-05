import pyodrx

class ExtendedOpenDrive(pyodrx.OpenDrive):
    

    def reset(self):
        """Reset only keeps road linkes, removes lane links, adjustments, adjusted geometries. Useful for editing and ODR
        """
        
        print(f"refreshing odr road adjustments")
        # TODO create a method to readjust in Extended Open Drive.
        for road in self.roads.values():
            road.reset()
        pass

    def resetAndReadjust(self):
        self.reset()
        self.adjust_roads_and_lanes()