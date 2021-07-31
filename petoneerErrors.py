class PetoneerAuthenticationError(Exception):
    
    """Exception raised for authentication errors while connecting to the Petoneer API.

    Attributes:
        http_code -- http code returned from HTTP request (eg: 200, 401, 500)
        username -- username used for authentication (optional)
        server_response_text -- server HTTP(s) response body [in raw text] (optional)
        message -- explanation of the error (optional)
    """

    def __init__(self, http_code, username="", server_response_text="", message="Authentication Error connecting to Petoneer API Server"):
        self.http_code = http_code
        self.username = username
        self.server_response_text = server_response_text
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'HTTP {self.http_code} -> Authentication Error: {self.message}\n -> usermame = "{self.username}"\n{self.server_response_text}'

class PetoneerServerError(Exception):
    """Exception raised for server errors produced from to the Petoneer API.

    Attributes:
        http_code -- http code returned from HTTP request (eg: 200, 401, 500)
        api_url -- requested URL of API server (optional)
        server_response_text -- server HTTP(s) response body [in raw text] (optional)
        message -- explanation of the error (optional)
    """

    def __init__(self, http_code, api_url = "SERVER", server_response_text = "", message="Server Error"):
        self.http_code = http_code
        self.url = api_url
        self.server_response_text = server_response_text
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'HTTP {self.http_code} -> Error returned from API Server "{self.url}: {self.message}\n{self.server_response_text}'

class PetoneerInvalidArgument(Exception):

    """Exception raised for invalid arguments / values provided to the Petoneer API module.

    Attributes:
        function_name -- module function that is raising the error
        argument_name -- argument passed to the function which has raised the error
        message -- explanation of the error (optional)
    """

    def __init__(self, function_name, argument_name, message="Invalid argument/value provided"):
        self.function_name = function_name
        self.argument_name = argument_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Petoneer.{self.function_name}() -> Invalid argument "{self.argument_name}": {self.message}'

class PetoneerInvalidServerResponse(Exception):
    """Exception raised when an unexpected or incomplete response is returned from the Petoneer API module.

    Attributes:
        http_code -- http code returned from HTTP request (eg: 200, 401, 500)
        api_url -- requested URL of API server (optional)
        server_response_text -- server HTTP(s) response body [in raw text] (optional)
        message -- explanation of the error (optional)
    """

    def __init__(self, http_code, api_url = "SERVER", server_response_text = "", message = "Invalid / incomplete response received from API server"):
        self.http_code = http_code
        self.url = api_url
        self.server_response_text = server_response_text
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'HTTP {self.http_code} -> Invalid response received from API server "{self.url}": {self.message}\n{self.server_response_text}'    

class PetoneerFountainDeviceOffline(Exception):
    """Exception raised for invalid arguments / values provided to the Petoneer API module.

    Attributes:
        fountain_serial_number -- serial_number of Fountain device that is reported by API as Offline
        api_server -- hostname of API server (optional)
        message -- explanation of the error (optional)
    """

    def __init__(self, fountain_serial_number, api_server = "SERVER", message="Fountain is powered off / not connected to the Internet"):
        self.fountain_serial_number = fountain_serial_number
        self.api_server = api_server
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Fountain (Serial #{self.fountain_serial_number}) is Offline [API Server: "{self.api_server}"]: {self.message}'

class PetoneerApiServerOffline(Exception):
    """Exception raised for invalid arguments / values provided to the Petoneer API module.

    Attributes:
        api_server -- hostname of API server
        http_code -- http code returned from HTTP request (optional)
        message -- explanation of the error (optional)
    """

    def __init__(self, api_server, http_code = 500, message="Server Offline"):
        self.api_server = api_server
        self.http_code = http_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'HTTP {self.http_code} -> Unable to connect to Petoneer API Server "{self.api_server}": {self.message}'
