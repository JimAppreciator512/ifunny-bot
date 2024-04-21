import pickle

# reading in headers
Headers = None
with open("headers.pickle", "rb") as fd:
    Headers = pickle.load(fd)

