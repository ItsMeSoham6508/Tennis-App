class EmptyFields(Exception):

    # Exception class to catch empty fields errors

    def __init__(self, indice: tuple | list | None, sheet_num: int | None, specific_field: str | None) -> None:
        if (indice is not None):
            message = f"Found missing field at indices {indice} in sheet {sheet_num}"

        if (indice is None):
            message = f"Found empty field: {specific_field}"

        super().__init__(message)


class DbConnectionNotFound(Exception):

    # Tell the user they aren't connected and perhaps should consider connecting

    def __init__(self, message="Not connected to database. Please hit connect in menu...") -> None:
        self.message = message
        super().__init__(self.message)
