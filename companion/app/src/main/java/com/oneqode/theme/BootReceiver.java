package com.oneqode.theme;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Re-applies the correct look and re-arms the schedule after a reboot. */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context ctx, Intent intent) {
        if (new Prefs(ctx).enabled()) {
            Scheduler.applyNowAndSchedule(ctx);
        }
    }
}
