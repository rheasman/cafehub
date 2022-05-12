# Installation

This assumes an Ubuntu system.

### Install python 3.8

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

sudo apt install python3.8
```
### Make your work env

cd into the place you have cloned the repo, and create your kivy environment

```
python -m virtualenv -p python 3.8 kivy_venv
```

Create a direct link to the activate script, for convenience
```
ln -s kivy_venv/bin/activate
```

Run the script to enter the environment:
```
source ./activate
```

### Install dependencies

Only do this after having run "activate".

```
pip3 install cython
pip3 install kivy
pip3 install oscpy
pip3 install bleak
pip3 install pydantic
pip3 install websocket-server
pip3 install jnius
pip3 install pytest
```

### Android APK

To build and run the Android APK on an Android device connected using debug mode on USB:
```
buildozer android debug deploy run && adb logcat  | grep -Ei "python|bleservice|AndroidRuntime"
```

The logcat and grep provides a way to watch the debug output of the program.

To try to connect to CafeHub, run it on the Android device. CafeHub will display its IP address.
Connect to that ip:5000 on a modern web browser to see a test app that talks to the DE1 via CafeHub.

### Running directly from the Linux CLI

To run CafeHub in the CLI, having made sure to run the activate script first:
```
cd src
python3 main.py
```
Connect to localhost:5000 to try the default test app.