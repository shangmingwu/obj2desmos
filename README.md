# obj2desmos
A script for converting a Wavefront .obj file into a format suitable for rendering in [3D Desmos](https://www.desmos.com/3d).

Clone the repository somewhere convenient, and optionally install `pyperclip` to support clipboard insertion.

```
pip install pyperclip
git clone https://github.com/shangmingwu/obj2desmos.git
```

## Usage

```
python port-obj.py [-cdf] [path to .obj file]
```

Options:
- `-c`: print console commands to stdout
- `-d`: copy equations directly to clipboard
- `-f`: print console commands to a file

Use only one of these at once. The script is pretty brittle.

Once you've run the script, go to [3D Desmos](https://www.desmos.com/3d) and either paste the given console commands into the JavaScript console, or paste the given equations directly into the expressions list.
