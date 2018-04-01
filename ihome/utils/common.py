from werkzeug.routing import BaseConverter

class RegxConverter(BaseConverter):

    def __init__(self,*args):
        super(RegxConverter, self).__init__()
        self.regex = args[0]