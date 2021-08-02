from copy import copy

class Combinator:


    @staticmethod
    def nP2(items):
        """Permutations of pairs

        Args:
            items ([type]): [description]
        """

        if len(items) < 2:
            raise Exception(f"Combinator: items cannot be less than 2")

        permutations = []

        for chosenItem in items:
            itemsWithoutchosenItem = copy(items)
            itemsWithoutchosenItem.remove(chosenItem)

            for secondItem in itemsWithoutchosenItem:
                permutations.append((chosenItem, secondItem))
        
        return permutations
