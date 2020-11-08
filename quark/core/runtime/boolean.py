class BooleanObject(int):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, bool(args[0]))
