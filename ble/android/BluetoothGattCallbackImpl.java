package org.decentespresso.dedebug;

import java.net.ConnectException;
import java.util.concurrent.CancellationException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.HashMap;
import java.util.UUID;

import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothProfile;


public final class BluetoothGattCallbackImpl extends BluetoothGattCallback
{
    public interface Interface {
        public void onConnectionStateChange(int status, int newState);
        public void onServicesDiscovered(int status);
        public void onCharacteristicChanged(String uuid, byte[] value);
        public void onCharacteristicRead(String uuid, int status, byte[] value);
        public void onCharacteristicWrite(String uuid, int status);
        public void onDescriptorRead(String uuid, int status, byte[] value);
        public void onDescriptorWrite(String uuid, int status);
    }
    private Interface callback;
        
    public void setImpl(Interface cbinterface) {
        callback = cbinterface;
    }        

    @Override
    public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
        callback.onConnectionStateChange(status, newState);
    }

    @Override
    public void onServicesDiscovered(BluetoothGatt gatt, int status) {
        callback.onServicesDiscovered(status);
    }

    @Override
    public void onCharacteristicRead(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
        callback.onCharacteristicRead(characteristic.getUuid().toString(), status, characteristic.getValue());
    }

    @Override
    public void onCharacteristicWrite(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
        callback.onCharacteristicWrite(characteristic.getUuid().toString(), status);
    }

    @Override
    public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
        callback.onCharacteristicChanged(characteristic.getUuid().toString(), characteristic.getValue());
    }

    @Override
    public void onDescriptorRead(BluetoothGatt gatt, BluetoothGattDescriptor descriptor, int status) {
        callback.onDescriptorRead(descriptor.getUuid().toString(), status, descriptor.getValue());
    }

    @Override
    public void onDescriptorWrite(BluetoothGatt gatt, BluetoothGattDescriptor descriptor, int status) {
        callback.onDescriptorWrite(descriptor.getUuid().toString(), status);
    }
}