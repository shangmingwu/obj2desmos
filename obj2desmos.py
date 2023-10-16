import logging
from argparse import ArgumentParser, FileType
from enum import Enum
from io import TextIOWrapper
from pathlib import Path
from typing import Generic, NamedTuple, TypeVar

logging.basicConfig(format="%(levelname)s: %(message)s")

try:
    import pyperclip
except ImportError:
    pyperclip = None
    logging.warning("pyperclip not found. copying to clipboard will not be available.")


"""
This is going unused for now. Folder creation through the console is iffy.

def makeFolderCmd(name: str, id: str) -> str:
    part1 = 'state = Calc.getState()\nstate.expressions.list.push({type: "folder", title: "'
    part2 = '", id: "'
    part3 = '"})\nCalc.setState(state)'
    return part1 + name + part2 + id + part3
"""

T = TypeVar("T")


class Option(Enum):
    CONSOLE = 0
    DIRECT = 1
    FILE = 2


class XYZLists(NamedTuple, Generic[T]):
    x: list[T]
    y: list[T]
    z: list[T]


def parse_args() -> tuple[Option, TextIOWrapper]:
    parser = ArgumentParser(
        prog="obj2desmos",
        description="Convert an .obj file to javascript commands for Desmos 3D.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-c",
        "--console",
        action="store_true",
        help="print console commands to stdout",
    )
    if pyperclip is not None:
        group.add_argument(
            "-d",
            "--direct",
            action="store_true",
            help="copy equations directly to clipboard",
        )
    group.add_argument(
        "-f",
        "--file",
        action="store_true",
        help="print console commands to a file",
    )
    parser.set_defaults(file=True)

    parser.add_argument("path", help="path to .obj file", type=FileType("r"))

    args = parser.parse_args()

    if args.console:
        return Option.CONSOLE, args.path
    elif pyperclip is not None and args.direct:
        return Option.DIRECT, args.path
    elif args.file:
        return Option.FILE, args.path

    return Option.FILE, args.path


def make_expression_cmd(id: str, latex: str) -> str:
    return (
        f'Calc.setExpressions([{{type: "expression", id: "{id}", latex: "{latex}"}}])'
    )


def parse_obj(file: TextIOWrapper) -> tuple[XYZLists[str], XYZLists[int]]:
    vertices = XYZLists[str]([], [], [])

    # triangle indices
    triangles = XYZLists[int]([], [], [])

    for i, line in enumerate(file):
        if line.startswith("v "):
            # vertex

            # v <x> <y> <z>
            line = line.split()[1:]

            # to correct for how blender vs desmos handles the z axis
            vertices.x.append(line[0])
            vertices.y.append(line[2])
            vertices.z.append(line[1])
        elif line.startswith("f "):
            # face

            # for now only care about the face
            # worry about texture later
            line = line.split()[1:]

            # technically there can be more sides than 3 on a face
            # but for now we only care about triangles

            # naively take the first 3 vertices and ignore the rest
            t1 = int(line[0].split("/")[0])
            t2 = int(line[1].split("/")[0])
            t3 = int(line[2].split("/")[0])

            if t1 < 0:
                t1 += len(vertices.x)
            if t2 < 0:
                t2 += len(vertices.x)
            if t3 < 0:
                t3 += len(vertices.x)

            triangles.x.append(t1)
            triangles.y.append(t2)
            triangles.z.append(t3)

    return vertices, triangles


def main():
    option, file = parse_args()
    vertices, triangles = parse_obj(file)

    v1_exp = make_expression_cmd("v1", f'v_1=[{",".join(vertices.x)}]')
    v2_exp = make_expression_cmd("v2", f'v_2=[{",".join(vertices.y)}]')
    v3_exp = make_expression_cmd("v3", f'v_3=[{",".join(vertices.z)}]')

    t1_exp = make_expression_cmd("t1", f't_1=[{",".join(map(str, triangles.x))}]')
    t2_exp = make_expression_cmd("t2", f't_2=[{",".join(map(str, triangles.y))}]')
    t3_exp = make_expression_cmd("t3", f't_3=[{",".join(map(str, triangles.z))}]')

    cons_latex = (
        r"\\left[\\operatorname{triangle}\\left(\\left(v_{1}\\left[t_{1}\\left[x\\right]\\right],v_{2}\\left[t_{1}\\left[x\\right]\\right],v_{3}\\left[t_{1}\\left[x\\right]\\right]\\right),\\left(v_{1}\\left[t_{2}\\left[x\\right]\\right],v_{2}\\left[t_{2}\\left[x\\right]\\right],v_{3}\\left[t_{2}\\left[x\\right]\\right]\\right),\\left(v_{1}\\left[t_{3}\\left[x\\right]\\right],v_{2}\\left[t_{3}\\left[x\\right]\\right],v_{3}\\left[t_{3}\\left[x\\right]\\right]\\right)\\right)\\operatorname{for}x=\\left[1,...,"
        + str(len(vertices.x))
        + r"\\right]\\right]"
    )

    cons_exp = make_expression_cmd("cons", cons_latex)

    commands = (v1_exp, v2_exp, v3_exp, t1_exp, t2_exp, t3_exp, cons_exp)

    if option == Option.CONSOLE:
        print(*commands, sep="\n")
    elif option == Option.FILE:
        path = Path(file.name).with_suffix(".commands")

        with open(path, "w") as f:
            print(*commands, sep="\n", file=f)

        logging.info(f"copy the contents of {path} into the JS console on Desmos.")
    elif option == Option.DIRECT and pyperclip is not None:
        pyperclip.copy("\n".join(commands))
        logging.info("commands copied to clipboard. paste into the JS console.")


if __name__ == "__main__":
    main()
