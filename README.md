# Python Efun alternatives package for LDMud

These are python efuns that mirror internal efuns of LDMud.

They can be used as a starting point to modify their behavior or to add
to an already running LDMud instance that was compiled without these.

This package contains the following efuns:
 * `json` module:
    * `mixed json_parse(string jsonstring)`
    * `string json_serialize(mixed data)`

## Usage

### Install from the python package index

The efun package can be downloaded from the python package index:

```
pip3 install --user ldmud-efun-alternatives
```

### Build & install the package yourself

You can build the package yourself.

First clone the repository
```
git clone https://github.com/ldmud/python-efun-alternatives.git
```

Install the package
```
cd python-efun-alternatives
python3 setup.py install --user
```

### Automatically load the modules at startup

Also install the [LDMud Python efuns](https://github.com/ldmud/python-efuns) and use its
[startup.py](https://github.com/ldmud/python-efuns/blob/master/startup.py) as the Python startup script for LDMud.
It will automatically detect the installed Python efuns and load them.

### Manually load the modules at startup

Add the following lines to your startup script:
```
import ldmudefunalternatives.json

ldmudefunalternatives.json.register()
```

Have fun!
