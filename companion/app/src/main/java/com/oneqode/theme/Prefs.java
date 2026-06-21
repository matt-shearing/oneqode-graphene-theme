package com.oneqode.theme;

import android.content.Context;
import android.content.SharedPreferences;

/** Simple SharedPreferences wrapper for the OneQode Theme settings. */
public final class Prefs {
    private static final String FILE = "oneqode_theme";

    public static final String MODE_SOLAR = "solar";
    public static final String MODE_FIXED = "fixed";

    private final SharedPreferences sp;

    public Prefs(Context ctx) {
        sp = ctx.getSharedPreferences(FILE, Context.MODE_PRIVATE);
    }

    public boolean enabled()          { return sp.getBoolean("enabled", true); }
    public String  mode()             { return sp.getString("mode", MODE_FIXED); }
    public float   lat()              { return sp.getFloat("lat", -33.8688f); }   // Sydney default
    public float   lng()              { return sp.getFloat("lng", 151.2093f); }
    public String  dayStart()         { return sp.getString("dayStart", "07:00"); }
    public String  nightStart()       { return sp.getString("nightStart", "19:00"); }
    public boolean switchAccent()     { return sp.getBoolean("accent", true); }
    public boolean switchWallpaper()  { return sp.getBoolean("wallpaper", true); }

    public void save(boolean enabled, String mode, float lat, float lng,
                     String dayStart, String nightStart,
                     boolean accent, boolean wallpaper) {
        sp.edit()
          .putBoolean("enabled", enabled)
          .putString("mode", mode)
          .putFloat("lat", lat)
          .putFloat("lng", lng)
          .putString("dayStart", dayStart)
          .putString("nightStart", nightStart)
          .putBoolean("accent", accent)
          .putBoolean("wallpaper", wallpaper)
          .apply();
    }
}
