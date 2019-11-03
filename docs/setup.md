# Setup

## Conda

```
git clone https://github.com/vframeio/vframe_synthetic
cd vframe_synthetic/cli
conda env create -f environment.yml
```

## Blender Installation and Setup

See [blender-setup.md](blender-setup.md)

## Test

Once you've installed the dependencies try running

```
cd cli
python cli_blender.py demo --blend ../data_store/blender/vframe_danger_sign_static_public.blend --python app/blender/demos/parse_demo.py
```

The output should be similar to:

```
NFO     test.py:36:cli() Running Blender test
Blender 2.80
Read prefs: /home/user/.config/blender/2.80/config/userpref.blend
found bundled python: /home/user/code/blender-2.80-linux-glibc217-x86_64/2.80/python
Read blend: /data_store/blender/vframe_danger_sign_static_public.blend
INFO     parse_demo.py:63:<module>() Running: parse_demo.py
INFO     parse_demo.py:64:<module>() Parse demo successful

Blender quit
```

