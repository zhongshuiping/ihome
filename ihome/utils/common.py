from werkzeug.routing import BaseConverter

class RegxConverter(BaseConverter):

    def __init__(self,map,*args):
        super(RegxConverter, self).__init__(map)
        self.regex = args[0]