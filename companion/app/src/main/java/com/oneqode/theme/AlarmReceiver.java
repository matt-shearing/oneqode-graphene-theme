package com.oneqode.theme;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Fires at each scheduled day/night boundary: applies the look and reschedules. */
public class AlarmReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context ctx, Intent intent) {
        Scheduler.applyNowAndSchedule(ctx);
    }
}
