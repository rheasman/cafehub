package org.decentespresso.cafehub;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;

public class RemoteDevFix {
  public BluetoothDevice getRDFromString(BluetoothAdapter adapter, String address) {
    return adapter.getRemoteDevice(address);
  }

  public BluetoothDevice getRDFromByte(BluetoothAdapter adapter, byte[] address) {
    return adapter.getRemoteDevice(address);
  }
}

