class meme:
    """Typeof meme"""
    def __init__(self, serialized: str) -> None:
        params = serialized.split(",")
        self.id = int(params[0])
        self.author = int(params[1])
        self.link = params[2]
    
    def serialize(self) -> str:
        return str(self.id) + ',' + str(self.author) +',' + self.link
    