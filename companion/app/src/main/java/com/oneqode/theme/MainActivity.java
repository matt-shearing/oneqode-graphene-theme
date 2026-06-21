package com.oneqode.theme;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.text.InputType;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.ScrollView;
import android.widget.TextView;

/**
 * OneQode Theme control panel: pick solar/fixed schedule, what to switch
 * (accent / wallpaper), apply manually, and see whether the one-time ADB grant
 * is in place.
 */
public class MainActivity extends Activity {

    private static final int BG = Color.parseColor("#11131d");
    private static final int CARD = Color.parseColor("#1a1f2e");
    private static final int CYAN = Color.parseColor("#34d6ff");
    private static final int PINK = Color.parseColor("#ff4d9d");
    private static final int INK = Color.parseColor("#dfeefc");
    private static final int MUTED = Color.parseColor("#8aa0b8");

    private RadioGroup modeGroup;
    private EditText latE, lngE, dayE, nightE;
    private CheckBox accentCb, wallCb, enabledCb;
    private TextView status, permWarn;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        Prefs p = new Prefs(this);

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(BG);
        LinearLayout root = col();
        int pad = dp(22);
        root.setPadding(pad, dp(40), pad, dp(40));

        root.addView(h1("OneQode Theme"));
        root.addView(muted("Automatic day / night for GrapheneOS — accent + wallpaper."));

        // permission banner
        permWarn = new TextView(this);
        permWarn.setPadding(dp(16), dp(16), dp(16), dp(16));
        permWarn.setTextColor(INK);
        permWarn.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
        permWarn.setBackgroundColor(Color.parseColor("#3a1230"));
        root.addView(spacer(16));
        root.addView(permWarn);

        // mode
        root.addView(spacer(20));
        root.addView(label("Schedule"));
        modeGroup = new RadioGroup(this);
        RadioButton solar = radio("Solar (sunrise / sunset)");
        RadioButton fixed = radio("Fixed times");
        solar.setId(1); fixed.setId(2);
        modeGroup.addView(solar); modeGroup.addView(fixed);
        modeGroup.check(Prefs.MODE_SOLAR.equals(p.mode()) ? 1 : 2);
        root.addView(modeGroup);

        // solar fields
        root.addView(label("Latitude / Longitude (solar)"));
        LinearLayout latlng = row();
        latE = input(String.valueOf(p.lat()), true);
        lngE = input(String.valueOf(p.lng()), true);
        latlng.addView(latE, lp1()); latlng.addView(spacerW(10)); latlng.addView(lngE, lp1());
        root.addView(latlng);

        // fixed fields
        root.addView(label("Day start / Night start (fixed, HH:MM)"));
        LinearLayout times = row();
        dayE = input(p.dayStart(), false);
        nightE = input(p.nightStart(), false);
        times.addView(dayE, lp1()); times.addView(spacerW(10)); times.addView(nightE, lp1());
        root.addView(times);

        // what to switch
        root.addView(spacer(18));
        root.addView(label("Switch"));
        accentCb = check("Accent colour (cyan ↔ pink)", p.switchAccent());
        wallCb = check("Wallpaper (Light Glass ↔ Night Ride)", p.switchWallpaper());
        enabledCb = check("Automatic switching enabled", p.enabled());
        root.addView(accentCb); root.addView(wallCb); root.addView(enabledCb);

        // buttons
        root.addView(spacer(22));
        Button save = button("Save & schedule", CYAN);
        save.setOnClickListener(v -> { savePrefs(); status.setText(Scheduler.applyNowAndSchedule(this)); refreshPerm(); });
        root.addView(save);

        LinearLayout manual = row();
        Button dayBtn = button("Apply Day now", CYAN);
        Button nightBtn = button("Apply Night now", PINK);
        dayBtn.setOnClickListener(v -> { savePrefs(); status.setText(OneQodeTheme.apply(this, true, accentCb.isChecked(), wallCb.isChecked())); refreshPerm(); });
        nightBtn.setOnClickListener(v -> { savePrefs(); status.setText(OneQodeTheme.apply(this, false, accentCb.isChecked(), wallCb.isChecked())); refreshPerm(); });
        manual.addView(dayBtn, lp1()); manual.addView(spacerW(10)); manual.addView(nightBtn, lp1());
        root.addView(spacer(10));
        root.addView(manual);

        // status
        root.addView(spacer(18));
        status = new TextView(this);
        status.setTextColor(MUTED);
        status.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
        status.setText("Ready.");
        root.addView(status);

        root.addView(spacer(16));
        TextView note = muted("Light/dark UI is handled by GrapheneOS's built-in Dark "
            + "theme schedule (Settings → Display → Dark theme → Schedule). Align it to "
            + "the same sunrise/sunset for a fully synced day/night.");
        root.addView(note);

        scroll.addView(root, new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        setContentView(scroll);
        refreshPerm();
    }

    private void refreshPerm() {
        if (OneQodeTheme.hasSecurePermission(this)) {
            permWarn.setBackgroundColor(Color.parseColor("#10331f"));
            permWarn.setText("✓ Accent control granted. Day/night will set the Material You accent.");
        } else {
            permWarn.setBackgroundColor(Color.parseColor("#3a1230"));
            permWarn.setText("⚠ One-time setup needed for accent switching. Run from a computer:\n\n"
                + "adb shell pm grant " + getPackageName()
                + " android.permission.WRITE_SECURE_SETTINGS\n\n"
                + "(No root. Wallpaper switching works without it.)");
        }
    }

    private void savePrefs() {
        String mode = modeGroup.getCheckedRadioButtonId() == 1 ? Prefs.MODE_SOLAR : Prefs.MODE_FIXED;
        float lat = parseF(latE.getText().toString(), -33.8688f);
        float lng = parseF(lngE.getText().toString(), 151.2093f);
        new Prefs(this).save(enabledCb.isChecked(), mode, lat, lng,
                norm(dayE.getText().toString(), "07:00"),
                norm(nightE.getText().toString(), "19:00"),
                accentCb.isChecked(), wallCb.isChecked());
    }

    // ---- tiny view helpers ----
    private LinearLayout col() { LinearLayout l = new LinearLayout(this); l.setOrientation(LinearLayout.VERTICAL); return l; }
    private LinearLayout row() { LinearLayout l = new LinearLayout(this); l.setOrientation(LinearLayout.HORIZONTAL); return l; }
    private LinearLayout.LayoutParams lp1() { return new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f); }
    private View spacer(int h) { View v = new View(this); v.setLayoutParams(new LinearLayout.LayoutParams(1, dp(h))); return v; }
    private View spacerW(int w) { View v = new View(this); v.setLayoutParams(new LinearLayout.LayoutParams(dp(w), 1)); return v; }

    private TextView h1(String s) { TextView t = new TextView(this); t.setText(s); t.setTextColor(CYAN); t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 28); return t; }
    private TextView label(String s) { TextView t = new TextView(this); t.setText(s); t.setTextColor(INK); t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15); t.setPadding(0, dp(16), 0, dp(6)); return t; }
    private TextView muted(String s) { TextView t = new TextView(this); t.setText(s); t.setTextColor(MUTED); t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13); t.setPadding(0, dp(4), 0, 0); return t; }

    private RadioButton radio(String s) { RadioButton r = new RadioButton(this); r.setText(s); r.setTextColor(INK); return r; }
    private CheckBox check(String s, boolean on) { CheckBox c = new CheckBox(this); c.setText(s); c.setTextColor(INK); c.setChecked(on); c.setPadding(0, dp(6), 0, dp(6)); return c; }

    private EditText input(String s, boolean numeric) {
        EditText e = new EditText(this);
        e.setText(s); e.setTextColor(INK); e.setHintTextColor(MUTED);
        e.setBackgroundColor(CARD); e.setPadding(dp(12), dp(12), dp(12), dp(12));
        e.setInputType(numeric ? (InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL | InputType.TYPE_NUMBER_FLAG_SIGNED) : InputType.TYPE_CLASS_DATETIME);
        return e;
    }

    private Button button(String s, int color) {
        Button b = new Button(this);
        b.setText(s); b.setAllCaps(false);
        b.setTextColor(Color.parseColor("#0b0d14"));
        b.setBackgroundColor(color);
        return b;
    }

    private int dp(int v) { return Math.round(getResources().getDisplayMetrics().density * v); }
    private float parseF(String s, float d) { try { return Float.parseFloat(s.trim()); } catch (Exception e) { return d; } }
    private String norm(String s, String d) { s = s.trim(); return s.matches("\\d{1,2}:\\d{2}") ? s : d; }
}
