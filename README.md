CafeHub
=
**Work in progress. No releases have been made yet**

CafeHub is a one-stop project that provides the following:
  * A Python3 interpreter that runs in Android.
  * A Bluetooth BLE API that runs on top of the stacks available in Android, Linux, Windows, or MacOS.
    * The API works around and hides all known Android BLE stack reliability issues.
    * The API provides both synchronous and asychronous APIs.
  * A working Python Kivy GUI environment for Android, MacOS, Windows, and Linux.
  * A static web server.
  * A web server with WebSocket support that provides a web abstraction to the host device BLE stack.

Applications
===
CafeHub is meant to support the following kinds of applications:
  * Using a phone, tablet, laptop, Raspberry Pi, etc. to provide a Javascript Web GUI to a Bluetooth device.
  * Running a Python-native GUI directly on a tablet that can talk to a BLE device.
  * Running a Python-native GUI on Linux, MacOS, Windows, Android, that can talk to a BLE device.

The name is CafeHub, as I intend this to be used to give owners of the Decent Espresso DE1 Espresso Machine a way to write their own applications for the machine. But, it can be used with any BLE device.

The Decent Espresso DE1 comes with an Android tablet, which commands the DE1 firmware to execute shot programs (and other operations) over BLE. CafeHub allows easy development of alternative user interfaces, by allowing a web browser to connect to its static web server and run javascript programs that can access the tablet BLE through websockets. The web client can run on the tablet along with the server, or it can be running on something like a phone or desktop.

Alternatively, UIs can be written directly in Python using the Kivy environment. Using SimpleSSHD and fuse-ssh or WinSCP, it's easy to modify python code directly on an Android tablet.

As I was developing this, I decided that it would be useful to not just run on Android, so the backend is capable of talking to the Bleak BLE library, which runs on Windows, MacOS, and Linux. This should allow quick and easy development on a desktop, rather than having to go through a long and slow APK packaging process to ship an Android APK.

Current State
===
This is a work in progress, and there is still much to do.
 * BLE operations are working on both Android and Linux, but not all operations have been implemented in both.
 * Some error exceptions generated from Bleak and Android have to be mapped to platform-agnostic equivalents.
 * Complete tests need to be written for both the sync and async APIs.
 * Kivy is working, and can run asynchronously or synchronously with the BLE API.
 * The websocket server is not implemented yet.

On the shoulders of giants...
===
This application is possible only because of work done by many before me:
  * Buildozer, which provides a convenient build environment that builds Android apps.
  * Python For Android, which is what I use to provide python support in Android.
  * Pyjnius, which allows me to create Java VM objects in Python.
  * Kivy, which provides a nice touch-surface-aware UI for Python programs.
  * Bleak, which gives me a BLE API that I can use on Windows, Linux and MacOS.
  
  
