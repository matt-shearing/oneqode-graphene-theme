package com.oneqode.theme;

import android.app.WallpaperManager;
import android.content.Context;
import android.content.pm.PackageManager;
import android.provider.Settings;

import java.io.InputStream;

/**
 * Core OneQode theming actions. Applies a "day" (Light Glass) or "night"
 * (Night Ride) look:
 *   - Material You accent  -> Settings.Secure (needs WRITE_SECURE_SETTINGS,
 *     granted once via ADB; no root).
 *   - Wallpaper            -> WallpaperManager (normal SET_WALLPAPER permission).
 *
 * The system light/dark theme is left to GrapheneOS's built-in dark-theme
 * schedule (an app cannot flip global night mode without a privileged
 * permission) — align that schedule to the same sunrise/sunset.
 */
public final class OneQodeTheme {

    public static final String DAY_HEX = "00b4c8";    // Light Glass ice cyan
    public static final String NIGHT_HEX = "ff0080";  // Night Ride neon pink
    public static final String STYLE = "VIBRANT";

    private static final String KEY =
            "theme_customization_overlay_packages";

    private OneQodeTheme() {}

    public static boolean hasSecurePermission(Context ctx) {
        return ctx.checkSelfPermission(android.Manifest.permission.WRITE_SECURE_SETTINGS)
                == PackageManager.PERMISSION_GRANTED;
    }

    /** Pin the Material You system palette to an exact hex. */
    public static boolean setAccent(Context ctx, String hex) {
        String json = "{"
                + "\"android.theme.customization.system_palette\":\"" + hex + "\","
                + "\"android.theme.customization.accent_color\":\"" + hex + "\","
                + "\"android.theme.customization.theme_style\":\"" + STYLE + "\","
                + "\"android.theme.customization.color_source\":\"preset\""
                + "}";
        try {
            return Settings.Secure.putString(ctx.getContentResolver(), KEY, json);
        } catch (SecurityException e) {
            return false;  // WRITE_SECURE_SETTINGS not granted yet
        }
    }

    /** Set the home + lock wallpaper from a bundled asset (day.png / night.png). */
    public static boolean setWallpaper(Context ctx, String assetName) {
        WallpaperManager wm = WallpaperManager.getInstance(ctx);
        try (InputStream in = ctx.getAssets().open(assetName)) {
            wm.setStream(in, null, true,
                    WallpaperManager.FLAG_SYSTEM | WallpaperManager.FLAG_LOCK);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /** Apply a full variant. Returns a short status string for the UI/log. */
    public static String apply(Context ctx, boolean day, boolean doAccent, boolean doWallpaper) {
        StringBuilder sb = new StringBuilder(day ? "Day (Light Glass): " : "Night (Night Ride): ");
        if (doAccent) {
            boolean ok = setAccent(ctx, day ? DAY_HEX : NIGHT_HEX);
            sb.append(ok ? "accent ok" : "accent FAILED (grant WRITE_SECURE_SETTINGS)");
        }
        if (doWallpaper) {
            boolean ok = setWallpaper(ctx, day ? "day.png" : "night.png");
            sb.append(doAccent ? ", " : "").append(ok ? "wallpaper ok" : "wallpaper FAILED");
        }
        if (!doAccent && !doWallpaper) sb.append("nothing enabled");
        return sb.toString();
    }
}
