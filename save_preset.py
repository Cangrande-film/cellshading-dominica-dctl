"""Save, rename or clear a User preset slot in Cellshading-Dominica.dctl.

    python save_preset.py SLOT --name "My Look" --values values.txt
    python save_preset.py SLOT --clear

values.txt holds one  name = value  per line, using the parameter names from the
DEFINE_UI_PARAMS lines (shadowThresh = 0.34). Missing ones keep their defaults.
Combo boxes take the item index, counting from 0.

The DCTL is edited in place and then copied to Resolve's LUT folder. In Resolve,
re-select the DCTL on the node (or Reset it) to load the new version.
"""
import argparse
import pathlib
import re
import shutil

HERE = pathlib.Path(__file__).resolve().parent
DCTL = HERE / "Cellshading-Dominica.dctl"
INSTALL = pathlib.Path(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\Killer7")
LABEL_OK = re.compile(r"^[A-Za-z0-9 :\-]{1,40}$")  # Resolve's parser chokes on ( ) , = "


def struct_fields(src):
    body = re.search(r"typedef struct \{(.*?)\} Cfg;", src, re.S).group(1)
    return {n: t for t, n in re.findall(r"(float|int) (\w+);", body)}


def read_values(path, fields):
    vals = {}
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        k, v = (s.strip() for s in line.split("=", 1))
        if k not in fields:
            raise SystemExit(f"unknown parameter: {k}")
        vals[k] = f"{float(v)!r}f" if fields[k] == "float" else str(int(float(v)))
    return vals


def slot_code(n, name, vals):
    if vals is None:
        return (f"// @user {n} begin  - empty slot: returns the sliders unchanged\n"
                f"__DEVICE__ Cfg userPreset{n}(Cfg P) {{\n    return P;\n}}\n// @user {n} end")
    lines = "".join(f"    P.{k} = {v};\n" for k, v in vals.items())
    return (f"// @user {n} begin  - {name}\n"
            f"__DEVICE__ Cfg userPreset{n}(Cfg P) {{\n    P = cfgDefaults();\n{lines}    return P;\n}}\n// @user {n} end")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slot", type=int)
    ap.add_argument("--name")
    ap.add_argument("--values")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--no-install", action="store_true")
    a = ap.parse_args()

    src = DCTL.read_text(encoding="utf-8")
    if not re.search(rf"// @user {a.slot} begin", src):
        raise SystemExit(f"no User slot {a.slot} in {DCTL.name}")
    name = f"User {a.slot}" if a.clear else (a.name or f"User {a.slot}")
    if not LABEL_OK.match(name):
        raise SystemExit("name: use only letters, digits, spaces, : and - (max 40)")

    vals = None if a.clear else read_values(a.values, struct_fields(src)) if a.values else None
    if not a.clear and vals is None and not a.name:
        raise SystemExit("give --values, --name or --clear")
    if vals is not None or a.clear:
        src = re.sub(rf"// @user {a.slot} begin.*?// @user {a.slot} end",
                     lambda _: slot_code(a.slot, name, vals), src, count=1, flags=re.S)

    # combo label: the slot's text in the Preset combo's label list
    m = re.search(r"(DEFINE_UI_PARAMS\(preset,.*\{.*\}, \{)(.*)(\}\))", src)
    labels = re.findall(r'"([^"]*)"', m.group(2))
    enums = re.search(r"\{ ([^}]*) \}", m.group(1)).group(1).split(", ")
    labels[enums.index(f"PR_USER{a.slot}")] = name
    src = src[:m.start(2)] + " " + ", ".join(f'"{l}"' for l in labels) + " " + src[m.end(2):]

    DCTL.write_text(src, encoding="utf-8")
    print(f"slot {a.slot}: {name}" + (f" ({len(vals)} values)" if vals else ""))
    if not a.no_install:
        shutil.copy2(DCTL, INSTALL / DCTL.name)
        print(f"installed to {INSTALL}")


if __name__ == "__main__":
    main()
