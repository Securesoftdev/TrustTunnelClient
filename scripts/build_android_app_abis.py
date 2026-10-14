#!/usr/bin/env python3
"""Build and verify the Android ABIs packaged by the SecureSoft client locally."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile


REPOSITORY = Path(__file__).resolve().parent.parent
ANDROID = REPOSITORY / "platform" / "android"
ABIS = ("arm64-v8a", "armeabi-v7a", "x86_64")


def first_line(*command: str) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return (result.stdout or result.stderr).splitlines()[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--abi", choices=ABIS, action="append", dest="selected_abis")
    args = parser.parse_args()
    selected_abis = args.selected_abis or ABIS
    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    source_sha = first_line("git", "-C", str(REPOSITORY), "rev-parse", "HEAD")
    android_home = Path(os.environ["ANDROID_HOME"])
    cmake_home = android_home / "cmake" / "3.31.6"
    ndk_properties = android_home / "ndk" / "28.1.13356709" / "source.properties"
    if not cmake_home.is_dir() or not ndk_properties.is_file():
        raise SystemExit("Android CMake 3.31.6 or NDK 28.1.13356709 is missing")
    (ANDROID / "local.properties").write_text(
        f"sdk.dir={android_home.as_posix()}\ncmake.dir={cmake_home.as_posix()}\n",
        encoding="utf-8",
    )
    gradlew = ANDROID / ("gradlew.bat" if os.name == "nt" else "gradlew")

    for abi in selected_abis:
        print(f"Building {abi} from {source_sha}", flush=True)
        subprocess.run(
            [str(gradlew), "assembleRelease", f"-PnativeAbi={abi}", "--no-daemon"],
            cwd=ANDROID,
            check=True,
        )
        aar = ANDROID / "lib" / "build" / "outputs" / "aar" / "lib-release.aar"
        if not aar.is_file():
            raise SystemExit(f"Missing release AAR for {abi}: {aar}")
        requested_member = f"jni/{abi}/libtrusttunnel_android.so"
        abi_output = output_root / abi
        abi_output.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(aar) as archive:
            native_members = sorted(
                name for name in archive.namelist()
                if name.startswith("jni/") and name.endswith(".so")
            )
            if native_members != [requested_member]:
                raise SystemExit(
                    f"Expected only {requested_member}; found {native_members}"
                )
            if archive.getinfo(requested_member).file_size == 0:
                raise SystemExit(f"Empty native library for {abi}")
            library = abi_output / "libtrusttunnel_android.so"
            library.write_bytes(archive.read(requested_member))
        aar_output = abi_output / f"TrustTunnelClient-android-{abi}-release.aar"
        shutil.copyfile(aar, aar_output)
        manifest = {
            "source_repository": "Securesoftdev/TrustTunnelClient",
            "source_sha": source_sha,
            "build_location": "local-windows",
            "abi": abi,
            "aar_sha256": sha256(aar_output),
            "so_sha256": sha256(library),
            "toolchain": {
                "python": first_line("python", "--version"),
                "conan": first_line("conan", "--version"),
                "go": first_line("go", "version"),
                "java": first_line("java", "-version"),
                "cmake": first_line("cmake", "--version"),
                "ninja": first_line("ninja", "--version"),
                "ndk": next(
                    line.partition("=")[2].strip()
                    for line in ndk_properties.read_text().splitlines()
                    if line.startswith("Pkg.Revision")
                ),
            },
        }
        (abi_output / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
