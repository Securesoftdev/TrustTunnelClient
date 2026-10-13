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

### Reproducing the arm64 CI build

The `Build Android arm64 adapter` GitHub Actions workflow runs the dependency
bootstrap above on Ubuntu with Python 3.13, Conan 2.12, Go 1.23.11, Rust 1.85,
JDK 17, Ninja 1.13, Android SDK 35, NDK 28.1.13356709 and CMake 3.31.6. It
then builds from the pull request's head commit using:

```bash
cd platform/android
./gradlew assembleRelease -PnativeAbi=arm64-v8a --no-daemon
```

`nativeAbi` is optional. Without it, the adapter keeps its normal ABI selection.
The workflow checks that the fresh release AAR contains exactly
`jni/arm64-v8a/libtrusttunnel_android.so`. Its seven-day CI artifact contains
the AAR, the extracted `.so`, and `manifest.json` with both SHA-256 hashes,
the source commit, workflow run, and toolchain versions. This artifact is for
integration testing only; the workflow does not publish a package.
