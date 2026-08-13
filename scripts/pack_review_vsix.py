#!/usr/bin/env python3
"""Build a .vsix (zip) for the Review UI. stdlib only — folder copy does not register in VS Code."""

from __future__ import annotations

import argparse
import json
import xml.sax.saxutils as sax
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "extensions" / "alexs-rig-review"
INCLUDE = ("package.json", "extension.js", "store.js", "README.md")


def load_pkg() -> dict:
    return json.loads((SRC / "package.json").read_text(encoding="utf-8"))


def manifest(pkg: dict) -> str:
    ident = sax.escape(str(pkg["name"]))
    ver = sax.escape(str(pkg["version"]))
    pub = sax.escape(str(pkg.get("publisher") or "alexbodner"))
    title = sax.escape(str(pkg.get("displayName") or ident))
    desc = sax.escape(str(pkg.get("description") or ""))
    engine = sax.escape(str((pkg.get("engines") or {}).get("vscode") or "^1.85.0"))
    deps = pkg.get("extensionDependencies") or []
    dep = sax.escape(",".join(deps))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="{ident}" Version="{ver}" Publisher="{pub}" />
    <DisplayName>{title}</DisplayName>
    <Description xml:space="preserve">{desc}</Description>
    <Tags></Tags>
    <Categories>Other</Categories>
    <GalleryFlags>Public</GalleryFlags>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="{engine}" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionDependencies" Value="{dep}" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="workspace" />
    </Properties>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
"""


CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
  <Default Extension=".xml" ContentType="text/xml"/>
  <Default Extension=".md" ContentType="text/markdown"/>
  <Default Extension=".js" ContentType="application/javascript"/>
</Types>
"""


def pack(out: Path) -> Path:
    pkg = load_pkg()
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("extension.vsixmanifest", manifest(pkg))
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        for name in INCLUDE:
            path = SRC / name
            if not path.is_file():
                raise FileNotFoundError(path)
            zf.write(path, f"extension/{name}")
    return out


def default_out() -> Path:
    pkg = load_pkg()
    return SRC / f"{pkg['name']}-{pkg['version']}.vsix"


def main() -> None:
    ap = argparse.ArgumentParser(description="Package alexs-rig-review as a .vsix")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    dest = args.out or default_out()
    pack(dest)
    print(dest)


if __name__ == "__main__":
    main()
