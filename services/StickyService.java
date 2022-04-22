package org.kivy.android;

public class StickyService extends org.kivy.android.PythonService {
  
  public int startType() {
    return 1; // START_STICKY; Causes JNI error if I try to use the static field name "START_STICKY"
  }
}
