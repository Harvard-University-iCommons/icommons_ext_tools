import os


def get_settings_file_name(settings_file):
    """ Returns just the name portion of settings_file, without file extension """
    return os.path.splitext(os.path.basename(settings_file))[0]
