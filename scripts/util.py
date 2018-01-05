def datafold(data):
    return [dict(zip(data["headers"], d)) for d in data["data"]]
