class ExecutorBuildException(Exception):
    PREFIX = "[SEAMLESS BUILD ERROR]"

    def __init__(self, message, *args, **kwargs):
        message = f"{self.PREFIX} {message}"
        super().__init__(message, *args, **kwargs)
