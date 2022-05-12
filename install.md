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

### Using CafeHub to serve files on Android

If CafeHub finds an index.html file in /sdcard/CafeHub/web, it will serve that directory over HTTP instead of the test app compiled into the APK.

I suggest installing the awesome [SimpleSSHD](http://www.galexander.org/software/simplesshd/) and using it to update files on your tablet.

To do this I normally install the open source F-Droid app store APK using adb, and then search in there.

**Setting up SimpleSSHD**

If no key is set in SimpleSSHD, then it generates a one-time password every time there is a connection attempt, and you have to manually copy the key off the screen into the password prompt. To make things easier, I copy my public key as an authorized key, to SimpleSSHD:

```
scp -P 2222 id_rsa.pub ray@192.168.68.90:authorized_keys
```

SimpleSSHD doesn't care what username you use.

Once this is done, in Linux, you can mount the directory on your tablet locally using:
```
sshfs ray@tab:/sdcard/ /home/ray/tabletfs/
```
Now you can simply treat the `tabletfs` directory as any other directory, and the files on the tablet will be updated as soon as they are changed locally.

In the past, in Windows, I found [WinSCP](https://winscp.net/eng/index.php) to be a good program for copying files to SSH servers. I haven't used it in a while.