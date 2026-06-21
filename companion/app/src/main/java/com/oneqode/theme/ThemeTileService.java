package com.oneqode.theme;

import android.graphics.drawable.Icon;
import android.service.quicksettings.Tile;
import android.service.quicksettings.TileService;

/**
 * Quick Settings tile: tap to toggle the OneQode look between day and night
 * manually (independent of the schedule — handy for a quick flip).
 */
public class ThemeTileService extends TileService {

    @Override
    public void onStartListening() {
        updateTile();
    }

    @Override
    public void onClick() {
        long now = System.currentTimeMillis();
        Prefs p = new Prefs(this);
        boolean currentlyDay;
        if (Prefs.MODE_SOLAR.equals(p.mode())) {
            currentlyDay = SolarClock.isDay(p.lat(), p.lng(), now);
        } else {
            currentlyDay = isDayFixed(p, now);
        }
        // flip to the opposite
        OneQodeTheme.apply(this, !currentlyDay, p.switchAccent(), p.switchWallpaper());
        updateTile();
    }

    private boolean isDayFixed(Prefs p, long now) {
        // reuse Scheduler's notion via a light recompute
        return new java.util.Date(now).getHours() >= hour(p.dayStart())
            && new java.util.Date(now).getHours() < hour(p.nightStart());
    }

    private int hour(String hhmm) {
        return Integer.parseInt(hhmm.split(":")[0]);
    }

    private void updateTile() {
        Tile t = getQsTile();
        if (t == null) return;
        long now = System.currentTimeMillis();
        Prefs p = new Prefs(this);
        boolean day = Prefs.MODE_SOLAR.equals(p.mode())
                ? SolarClock.isDay(p.lat(), p.lng(), now)
                : isDayFixed(p, now);
        t.setLabel(day ? "OneQode Day" : "OneQode Night");
        t.setIcon(Icon.createWithResource(this, R.drawable.ic_launcher_monochrome));
        t.setState(Tile.STATE_ACTIVE);
        t.updateTile();
    }
}
