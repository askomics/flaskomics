from askomics.libaskomics.Params import Params

class File(Params):

    def __init__(self, app, session, file_info):
        Params.__init__(self, app, session)
        self.name = file_info['name']
        self.path = file_info['path']
        self.type = file_info['type']
        self.size = file_info['size']

