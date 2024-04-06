import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ldmud-efun-alternatives",
    version="0.0.2",
    author="LDMud Team",
    author_email="ldmud-dev@UNItopia.DE",
    description="Python Efun alternatives package for LDMud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ldmud/python-efun-alternatives",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'ldmud_efun': [
              'json_serialize   = ldmudefunalternatives.json:efun_json_serialize',
              'json_parse       = ldmudefunalternatives.json:efun_json_parse',
              'sl_open          = ldmudefunalternatives.sqlite:efun_sl_open',
              'sl_close         = ldmudefunalternatives.sqlite:efun_sl_close',
              'sl_exec          = ldmudefunalternatives.sqlite:efun_sl_exec',
              'sl_insert_id     = ldmudefunalternatives.sqlite:efun_sl_insert_id',
        ]
    },
    zip_safe=False,
)
