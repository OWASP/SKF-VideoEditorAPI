import enum

class APIConstants:
    def __init__(self):
        pass

    class DeveloperAPIMessages(enum.Enum):
        DEVELOPER_API_RESPONSE_MESSAGE = "New user is sucessfully created"

    class AccessTokenMessages(enum.Enum):
        CREDENTIAL_NOT_FOUND = "Unable to authenticate with provided credentials"
        
