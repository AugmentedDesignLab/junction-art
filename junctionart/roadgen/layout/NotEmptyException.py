class NotEmptyException(Exception):

    def __init__(self, obj):
        super().__init__(obj)