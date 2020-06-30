# https://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d
