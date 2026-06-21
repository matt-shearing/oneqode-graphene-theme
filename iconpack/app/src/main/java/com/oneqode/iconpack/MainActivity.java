package com.oneqode.iconpack;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.text.Html;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/**
 * Minimal dashboard for the OneQode icon pack. The pack itself is pure
 * resources (appfilter.xml + drawables); this screen only explains how to apply
 * it, so the app opens to something branded instead of crashing.
 */
public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        int bg = Color.parseColor("#11131d");
        int accent = Color.parseColor("#34d6ff");
        int pink = Color.parseColor("#ff4d9d");
        int ink = Color.parseColor("#dfeefc");

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(bg);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        int pad = dp(28);
        root.setPadding(pad, dp(56), pad, dp(40));

        ImageView logo = new ImageView(this);
        logo.setImageResource(R.mipmap.ic_launcher_foreground);
        LinearLayout.LayoutParams lp =
                new LinearLayout.LayoutParams(dp(120), dp(120));
        logo.setLayoutParams(lp);
        root.addView(logo);

        root.addView(title("OneQode", accent, 34));
        root.addView(title("Icon Pack", ink, 20));

        TextView body = new TextView(this);
        body.setTextColor(ink);
        body.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
        body.setLineSpacing(dp(4), 1f);
        body.setPadding(0, dp(28), 0, 0);
        body.setText(Html.fromHtml(
            "<b>Apply with Lawnchair (recommended):</b><br>"
            + "1. Install Lawnchair from lawnchair.app<br>"
            + "2. Long-press home &rarr; Home settings &rarr; <b>General &rarr; Icon pack</b> &rarr; OneQode<br>"
            + "3. Enable <b>Themed icons</b> for the Material You look<br><br>"
            + "<b>Nova / Action / Apex:</b><br>"
            + "Settings &rarr; Look &amp; feel &rarr; Icon style / Icon theme &rarr; OneQode<br><br>"
            + "<b>Tip:</b> pair with the matching OneQode wallpaper and run "
            + "<i>oneqode-accent</i> over ADB to lock the system accent to the "
            + "OneQode colour.",
            Html.FROM_HTML_MODE_LEGACY));
        root.addView(body);

        scroll.addView(root, new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        setContentView(scroll);
    }

    private TextView title(String text, int color, int sp) {
        TextView t = new TextView(this);
        t.setText(text);
        t.setTextColor(color);
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, sp);
        t.setGravity(Gravity.CENTER);
        t.setPadding(0, dp(8), 0, 0);
        return t;
    }

    private int dp(int v) {
        return Math.round(getResources().getDisplayMetrics().density * v);
    }
}
