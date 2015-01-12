# from http://flask.pocoo.org/docs/0.10/patterns/apierrors/

class ServerException(Exception):
    def __init__(self, message, status_code=500, payload=None):
        super(ServerException, self).__init__(message)
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        if self.payload:
            return self.payload
        return dict(message=self.message,
                    status_code=self.status_code)
