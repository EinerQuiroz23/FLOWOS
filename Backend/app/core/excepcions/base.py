class FlowosException(Exception):
    """
    Excepción base para los errores controlados de FLOWOS.
    """

    def __init__(
        self,
        message: str,
        code: str = "FLOWOS_ERROR",
        status_code: int = 400
    ):
        self.message = message
        self.code = code
        self.status_code = status_code

        super().__init__(message)