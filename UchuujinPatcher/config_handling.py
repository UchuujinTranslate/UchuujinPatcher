# create config file here

# have function for first time setup
# ask intelligently if iso is correct and put into config
import ruamel.yaml
#import sys
from os import path

# Default config as string (for keeping comments)
default_config_str = """\
# UchuujinPatcher config

- iso:
    # Auto detect an .iso file in the root directory and ask if correct
    auto_detect: true
    
    # Select the first .iso found without asking. (Requires auto_detect)
    auto_select: false
    
    # Exact iso name to find in root directory (if auto_detect is disabled)
    iso_name: '2668 - Nichijou - Uchuujin (Japan) (v1.01).iso'

- emu_test:
    # Automatically open PPSSPP with patched .iso when done.
    # Must download and put PPSSPP in 'emu' folder!
    auto_test: false



# Advanced settings
# --------------
- cleanup:
    # If scripts delete the previous work folders
    enabled: true
    

    
# Debug settings
# --------------

# WARNING!
# In any normal environment, all these settings should be left as default. 
# Only disable these if you know what you are doing.

- multithreading:
    # Use multiple CPU cores to process through files several times faster.
    sc_patch_enabled: true
    
- debug_messages:
    # Whether to print large amounts of output.
    # Too much can cause process to complete slower.
    enabled: false

- processes:
    # Enable / disable different parts of the patching process.
    # Useful for when working on a specific process in the code.

    # sc.cpk processing
    sc_enabled: true

    # CG / union.cpk processing
    union_enabled: true
"""


yaml = ruamel.yaml.YAML()  # defaults to round-trip if no parameters given
default_config = yaml.load(default_config_str)

# print(code)
# yaml.dump(code, sys.stdout)

def config():
    if not path.exists("config.yml"):
        with open("config.yml", 'w') as f:
            yaml.dump(default_config, f)
        print('Created config!')

    with open('config.yml') as f:
        config = yaml.load(f)

    print('Loaded config.')
    #print(config)
    return config




if __name__ == "__main__":
    config()