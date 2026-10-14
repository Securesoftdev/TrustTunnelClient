# TrustTunnel Client Android adapter

## Build Instructions

### Prerequisites

- [Python 3](https://www.python.org/downloads/) 3.13 or higher
- [CMake](https://cmake.org/download/) 3.24 or higher
- [Conan](https://github.com/conan-io/conan/releases) 2.0.5 or higher
- [Go](https://go.dev/dl/) 1.18.3 or higher
- [Ninja](https://formulae.brew.sh/formula/ninja) 1.13 or higher
- [Android SDK](https://developer.android.com/tools/releases/platform-tools#downloads) 35.0.0 or higher
- [Android NDK](https://developer.android.com/ndk/downloads) 28.1.13356709 or higher

You can also download SDK and NDK using Android Studio SDK Manager.

### Building

To obtain all required conan dependencies, go to the root of the project and run:

```bash
python3 -m venv env
source env/bin/activate
pip3 install -r scripts/requirements.txt

scripts/bootstrap_conan_deps.py
```

Go to the Android adapter folder, set the CMake version to use and build the adapter:

```bash
cd platform/android

# Use system cmake, ensure `cmake` is in your path
echo cmake.dir=$(dirname $(dirname $(which cmake))) >> local.properties

./gradlew assembleRelease
# or ./gradlew assembleDebug
```

### Building SecureSoft client ABIs locally

The SecureSoft owner requires local builds on the workstation. Prepare Python
3.13, Conan 2.12, Go 1.23.11, Rust 1.85, JDK 17, Ninja 1.13, Android SDK 35,
NDK 28.1.13356709 and CMake 3.31.6, then run the dependency bootstrap from
the repository root. Build each ABI packaged by the client from one exact
source commit. On Windows, the repository helper verifies the AAR contents
and writes a local SHA/source manifest for each ABI:

```powershell
python scripts/build_android_app_abis.py --output-dir D:\trusttunnel-local-abis
```

The equivalent manual Gradle command for one ABI is:

```bash
cd platform/android
./gradlew assembleRelease -PnativeAbi=arm64-v8a --no-daemon
```

`nativeAbi` is optional. Without it, the adapter keeps its normal ABI selection.
Copy `lib/build/outputs/aar/lib-release.aar` after each manual build because
the next ABI overwrites that path. The helper checks each AAR for only its
requested `jni/<abi>/libtrusttunnel_android.so` and records SHA-256, source
commit, ABI, and local toolchain versions. The `Build Android app ABIs` workflow
is manual-only and must not be dispatched without the owner's explicit request.
No local build publishes a package by itself.
