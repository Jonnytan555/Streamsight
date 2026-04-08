from appsettings import engine


def get_db():
    # engine.begin() automatically commits on clean exit and rolls back on exception.
    # This replaces engine.connect() which required manual db.commit() calls
    # that could silently fail to persist if the connection closed first.
    with engine.begin() as conn:
        yield conn
