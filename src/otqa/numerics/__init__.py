"""Session-owned numerical operations, loaded only at numerical execution."""

__all__ = ["LinearProgramBackend", "LinearResult"]


def __getattr__(name):
    if name == "LinearResult":
        from otqa.models.numerical import LinearResult
        return LinearResult
    if name == "LinearProgramBackend":
        from .lp import LinearProgramBackend
        return LinearProgramBackend
    raise AttributeError(name)
