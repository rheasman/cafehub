package org.decentespresso.cafehub;
import android.bluetooth.le.*;
import java.util.List;

public class ScanCallbackImpl extends ScanCallback {
    public interface IScanCallback {  
        void onBatchScanResults(List<ScanResult> results);
        void onScanFailed(int errorCode);
        void onScanResult(int callbackType, ScanResult result);
    }

    private IScanCallback implem = null;

    public void setImpl(IScanCallback imp) {
        implem = imp;
    }
  
    public void onBatchScanResults(List<ScanResult> results) {
        if (implem != null) {
            implem.onBatchScanResults(results);
        }
    }

    public void onScanFailed(int errorCode) {
        if (implem != null) {
            implem.onScanFailed(errorCode);
        }
    }

    public void onScanResult(int callbackType, ScanResult result) {
        if (implem != null) {
            implem.onScanResult(callbackType, result);
        }
    }


}
