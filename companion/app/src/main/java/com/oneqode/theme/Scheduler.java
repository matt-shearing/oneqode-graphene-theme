package com.oneqode.theme;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;

import java.util.Calendar;

/**
 * Computes the current day/night state and the next switch time (solar or fixed),
 * applies the theme, and schedules the next wake-up via AlarmManager.
 * Uses setAndAllowWhileIdle (no exact-alarm permission needed) — minute-level
 * timing is plenty for a theme switch.
 */
public final class Scheduler {

    private static final long DAY_MS = 86_400_000L;

    private Scheduler() {}

    private static PendingIntent pi(Context ctx) {
        Intent i = new Intent(ctx, AlarmReceiver.class).setAction("com.oneqode.theme.SWITCH");
        return PendingIntent.getBroadcast(ctx, 42, i,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    /** Apply the look appropriate for "now", then schedule the next boundary. */
    public static String applyNowAndSchedule(Context ctx) {
        Prefs p = new Prefs(ctx);
        long now = System.currentTimeMillis();

        boolean day;
        long next;
        if (Prefs.MODE_SOLAR.equals(p.mode())) {
            day = SolarClock.isDay(p.lat(), p.lng(), now);
            next = SolarClock.nextBoundary(p.lat(), p.lng(), now)[0];
        } else {
            long dayStart = todayAt(p.dayStart(), now);
            long nightStart = todayAt(p.nightStart(), now);
            day = now >= dayStart && now < nightStart;
            if (now < dayStart)        next = dayStart;
            else if (now < nightStart) next = nightStart;
            else                       next = dayStart + DAY_MS;
        }

        String status = OneQodeTheme.apply(ctx, day, p.switchAccent(), p.switchWallpaper());

        if (p.enabled()) {
            AlarmManager am = ctx.getSystemService(AlarmManager.class);
            // guard against past/now times
            if (next <= now) next = now + 60_000L;
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, next, pi(ctx));
        }
        return status;
    }

    public static void cancel(Context ctx) {
        AlarmManager am = ctx.getSystemService(AlarmManager.class);
        am.cancel(pi(ctx));
    }

    private static long todayAt(String hhmm, long now) {
        String[] parts = hhmm.split(":");
        int h = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        Calendar c = Calendar.getInstance();
        c.setTimeInMillis(now);
        c.set(Calendar.HOUR_OF_DAY, h);
        c.set(Calendar.MINUTE, m);
        c.set(Calendar.SECOND, 0);
        c.set(Calendar.MILLISECOND, 0);
        return c.getTimeInMillis();
    }
}
