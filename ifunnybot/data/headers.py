import pickle

# reading in headers
Headers = None
with open("ifunnybot/data/headers.pickle", "rb") as fd:
    Headers = pickle.load(fd)

