class ConfigHandler:
    def get_config_value(self, file_name, conf_name):
        # Open file and set mode to "r" (Read)
        file = open(file_name, "r")
        # Split every config after new line, creating array of configs
        contents = file.read().split("\n")
        for config in contents:
            conf = config.split(" : ")
            # If conf name in contents equal conf name argument, return conf value
            if conf[0] == conf_name:
                return conf[1]
