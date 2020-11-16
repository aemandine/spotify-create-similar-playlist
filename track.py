class Track:

    """
    Constructor
    @input parameters: either a dictionary mapping parameters to values, or a list of values in order of PARAMETERS
    @input type (string): if "dict", then parameters should be read as a dictionary (from track audio_features)
                          if "list", then parameters should be read as a list of parameters (from songs.txt)
    """
    def __init__(self, parameters, type):
        if type == "dict":
            self.id = parameters["id"]
            self.features = parameters
        else:
            self.id = parameters[0]
            self.features = {}

            PARAMETERS = ["acousticness", "danceability", "energy", "instrumentalness", "liveness",
                          "valence", "speechiness", "mode", "tempo", "loudness"]
            for i in range(len(PARAMETERS)):
                self.features[PARAMETERS[i]] = float(parameters[i + 1])

    """
    Accessor method for self.id
    """
    def get_id(self):
        return self.id

    """
    Accessor method for any of the parameters
    """
    def get_parameter(self, feature_name):
        if feature_name not in self.features:
            print("Error: Feature " + feature_name + " not in feature list.")
            raise
        return self.features[feature_name]

    """
    @input feature_name (string): the name of the feature (e.g. liveness)
    @input med (float): floor of medium bucket
    @input high (float): floor of high bucket
    @return 0 if low, 1 if med, 2 if high
    """
    def get_bucket(self, feature_name, med, high):
        if feature_name not in self.features:
            print("Error: Feature " + feature_name + " not in feature list.")
            raise

        LOW = 0
        MED = 1
        HIGH = 2

        feature_value = self.features[feature_name]
        if feature_value >= high:
            return HIGH
        elif feature_value >= med:
            return MED
        else:
            return LOW
