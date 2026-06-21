#!/usr/bin/env python3
"""
Generate appfilter.xml, drawable.xml and grayscale_icon_map.xml for the OneQode
icon pack from a single mapping table.

  * appfilter.xml          ComponentInfo{pkg/activity} -> colour drawable (ic_*)
  * grayscale_icon_map.xml package -> monochrome drawable (ic_*_mono) [Lawnchair]
  * drawable.xml           catalogue for the launcher's manual icon picker

Only universal category glyphs are used (no third-party brand artwork). Where a
launch activity is uncertain across versions, multiple component variants are
listed. Gaps are easy to fill on-device with tools/dump-components.sh, which dumps
the user's actual launchable components.
"""
from pathlib import Path
from collections import OrderedDict

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "app" / "src" / "main" / "res" / "xml"

# (drawable_glyph, package, [launch activities...])
# activity "*" means: also emit a Nova/Lawnchair package-wildcard not supported,
# so we list the known activities explicitly.
MAP = [
    # ---- AOSP / GrapheneOS core ----
    ("phone", "com.android.dialer", ["com.android.dialer.main.impl.MainActivity",
                                     ".DialtactsActivity"]),
    ("phone", "com.google.android.dialer", ["com.google.android.dialer.extensions.GoogleDialtactsActivity"]),
    ("messages", "com.android.messaging", ["com.android.messaging.ui.conversationlist.ConversationListActivity"]),
    ("messages", "com.google.android.apps.messaging", ["com.google.android.apps.messaging.ui.ConversationListActivity"]),
    ("contacts", "com.android.contacts", ["com.android.contacts.activities.PeopleActivity"]),
    ("contacts", "com.google.android.contacts", ["com.google.android.apps.contacts.activities.PeopleActivity"]),
    ("camera", "app.grapheneos.camera", [".ui.activities.MainActivity", ".CapturerActivity"]),
    ("camera", "com.android.camera2", ["com.android.camera.CameraLauncher"]),
    ("photos", "com.android.gallery3d", ["com.android.gallery3d.app.GalleryActivity"]),
    ("clock", "com.android.deskclock", ["com.android.deskclock.DeskClock"]),
    ("clock", "com.google.android.deskclock", ["com.android.deskclock.DeskClock"]),
    ("calc", "com.android.calculator2", ["com.android.calculator2.Calculator"]),
    ("calc", "com.google.android.calculator", ["com.android.calculator2.Calculator"]),
    ("calendar", "com.android.calendar", ["com.android.calendar.AllInOneActivity"]),
    ("calendar", "com.google.android.calendar", ["com.google.android.calendar.LaunchActivity"]),
    ("settings", "com.android.settings", ["com.android.settings.Settings"]),
    ("files", "com.android.documentsui", ["com.android.documentsui.files.FilesActivity"]),
    ("files", "com.google.android.documentsui", ["com.android.documentsui.files.FilesActivity"]),
    ("pdf", "app.grapheneos.pdfviewer", [".MainActivity"]),
    ("store", "app.grapheneos.apps", [".ui.MainActivity", ".MainActivity"]),
    ("settings", "app.grapheneos.info", [".MainActivity"]),
    ("auth", "app.grapheneos.camera.qr", [".MainActivity"]),

    # ---- Browsers ----
    ("browser", "app.vanadium.browser", ["com.google.android.apps.chrome.Main",
                                         "org.chromium.chrome.browser.ChromeTabbedActivity"]),
    ("browser", "com.android.chrome", ["com.google.android.apps.chrome.Main"]),
    ("browser", "org.mozilla.firefox", ["org.mozilla.fenix.HomeActivity",
                                        "org.mozilla.gecko.BrowserApp"]),
    ("browser", "org.mozilla.fenix", ["org.mozilla.fenix.HomeActivity"]),
    ("browser", "com.brave.browser", ["com.google.android.apps.chrome.Main"]),
    ("browser", "com.duckduckgo.mobile.android", ["com.duckduckgo.app.launch.Launcher"]),
    ("browser", "com.opera.browser", ["com.opera.Opera"]),
    ("browser", "org.torproject.torbrowser", ["org.mozilla.fenix.HomeActivity"]),

    # ---- Google ----
    ("mail", "com.google.android.gm", ["com.google.android.gm.ConversationListActivityGmail"]),
    ("maps", "com.google.android.apps.maps", ["com.google.android.maps.MapsActivity"]),
    ("photos", "com.google.android.apps.photos", ["com.google.android.apps.photos.home.HomeActivity"]),
    ("store", "com.android.vending", ["com.android.vending.AssetBrowserActivity"]),
    ("play", "com.google.android.youtube", ["com.google.android.apps.youtube.app.WatchWhileActivity"]),
    ("music", "com.google.android.apps.youtube.music", ["com.google.android.apps.youtube.music.activities.MusicActivity"]),
    ("search", "com.google.android.googlequicksearchbox", ["com.google.android.googlequicksearchbox.SearchActivity",
                                                           "com.google.android.apps.search.googleapp.activity.GoogleAppActivity"]),
    ("notes", "com.google.android.keep", ["com.google.android.keep.activities.BrowseActivity"]),
    ("cloud", "com.google.android.apps.docs", ["com.google.android.apps.docs.drive.startup.StartupActivity"]),
    ("doc", "com.google.android.apps.docs.editors.docs", ["com.google.android.apps.docs.editors.homescreen.HomescreenActivity"]),
    ("sheet", "com.google.android.apps.docs.editors.sheets", ["com.google.android.apps.docs.editors.homescreen.HomescreenActivity"]),
    ("slides", "com.google.android.apps.docs.editors.slides", ["com.google.android.apps.docs.editors.homescreen.HomescreenActivity"]),
    ("translate", "com.google.android.apps.translate", ["com.google.android.apps.translate.TranslateActivity",
                                                        "com.google.android.apps.translate.HomeActivity"]),
    ("wallet", "com.google.android.apps.walletnfcrel", ["com.google.commerce.tapandpay.android.wallet.WalletActivity"]),
    ("wallet", "com.google.android.apps.wallet", ["com.google.commerce.tapandpay.android.wallet.WalletActivity"]),
    ("fitness", "com.google.android.apps.fitness", ["com.google.android.apps.fitness.MainActivity"]),
    ("podcast", "com.google.android.apps.podcasts", ["com.google.android.apps.podcasts.MainActivity"]),
    ("files", "com.google.android.apps.nbu.files", ["com.google.android.apps.nbu.files.home.HomeActivity"]),
    ("mic", "com.google.android.apps.recorder", ["com.google.android.apps.recorder.ui.records.RecordsActivity"]),
    ("video_call", "com.google.android.apps.tachyon", ["com.google.android.apps.tachyon.ui.main.MainActivity"]),
    ("ai", "com.google.android.apps.bard", ["com.google.android.apps.bard.MainActivity"]),
    ("weather", "com.google.android.apps.weather", ["com.google.android.apps.weather.PixelWeatherActivity"]),
    ("game", "com.google.android.play.games", ["com.google.android.gms.games.ui.destination.main.MainActivity"]),

    # ---- Messaging / social ----
    ("chat", "com.whatsapp", ["com.whatsapp.HomeActivity", "com.whatsapp.Main"]),
    ("secure_chat", "org.thoughtcrime.securesms", ["org.thoughtcrime.securesms.RoutingActivity",
                                                   ".RoutingActivity"]),
    ("secure_chat", "im.molly.app", [".RoutingActivity"]),
    ("chat", "org.telegram.messenger", ["org.telegram.ui.LaunchActivity"]),
    ("chat", "org.telegram.messenger.web", ["org.telegram.ui.LaunchActivity"]),
    ("social", "com.discord", ["com.discord.main.MainDefault"]),
    ("social", "com.facebook.katana", ["com.facebook.katana.LoginActivity"]),
    ("chat", "com.facebook.orca", ["com.facebook.orca.auth.StartScreenActivity"]),
    ("social", "com.instagram.android", ["com.instagram.android.activity.MainTabActivity"]),
    ("bird", "com.twitter.android", ["com.twitter.app.main.MainActivity"]),
    ("news", "com.reddit.frontpage", ["com.reddit.frontpage.MainActivity",
                                      "launcher.default"]),
    ("camera", "com.snapchat.android", ["com.snap.mushroom.MainActivity"]),
    ("social", "com.linkedin.android", ["com.linkedin.android.authenticator.LaunchActivity"]),
    ("photos", "com.pinterest", ["com.pinterest.activity.PinterestActivity"]),
    ("chat", "com.Slack", ["slack.features.home.HomeActivity", "com.Slack.ui.HomeActivity"]),
    ("video_call", "com.microsoft.teams", ["com.microsoft.skype.teams.Launcher"]),
    ("secure_chat", "im.vector.app", ["im.vector.app.features.Alias"]),
    ("secure_chat", "chat.simplex.app", [".MainActivity"]),
    ("chat", "com.mattermost.rn", ["com.mattermost.rnbeta.MainActivity", ".MainActivity"]),

    # ---- Media ----
    ("music", "com.spotify.music", ["com.spotify.music.MainActivity"]),
    ("video", "com.netflix.mediaclient", ["com.netflix.mediaclient.ui.launch.UIWebViewActivity"]),
    ("video", "tv.twitch.android.app", ["tv.twitch.android.feature.theatre.MainActivity",
                                        "tv.twitch.android.app.core.LandingActivity"]),
    ("music", "com.soundcloud.android", ["com.soundcloud.android.main.LauncherActivity"]),
    ("video", "com.plexapp.android", ["com.plexapp.plex.activities.SplashActivity"]),
    ("play", "org.videolan.vlc", ["org.videolan.vlc.StartActivity"]),
    ("music", "org.schabi.newpipe", ["org.schabi.newpipe.MainActivity"]),
    ("music", "com.bandcamp.android", ["com.bandcamp.android.home.HomeActivity"]),

    # ---- Finance ----
    ("wallet", "com.paypal.android.p2pmobile", ["com.paypal.android.p2pmobile.startup.activities.StartupActivity"]),
    ("bank", "com.coinbase.android", ["com.coinbase.android.SplashActivity"]),
    ("bank", "com.wise.android", ["com.wise.android.MainActivity"]),
    ("bank", "com.revolut.revolut", ["com.revolut.ui.splash.SplashActivity"]),
    ("wallet", "com.x.android", ["com.x.android.MainActivity"]),
    ("bank", "io.metamask", ["io.metamask.MainActivity"]),

    # ---- Dev / utilities ----
    ("terminal", "com.termux", ["com.termux.app.TermuxActivity"]),
    ("terminal", "com.termux.x11", ["com.termux.x11.MainActivity"]),
    ("git", "com.github.android", ["com.github.android.activities.MainActivity"]),
    ("store", "org.fdroid.fdroid", ["org.fdroid.fdroid.views.main.MainActivity"]),
    ("store", "com.aurora.store", ["com.aurora.store.MainActivity",
                                   "com.aurora.store.view.ui.splash.SplashActivity"]),
    ("store", "app.accrescent.client", [".MainActivity"]),
    ("cloud", "com.nextcloud.client", ["com.owncloud.android.ui.activity.FileDisplayActivity"]),
    ("vpn", "com.protonvpn.android", ["com.protonvpn.android.ui.SplashActivity",
                                      "com.protonvpn.android.ui.main.MobileMainActivity"]),
    ("vpn", "com.wireguard.android", ["com.wireguard.android.activity.MainActivity"]),
    ("vpn", "net.mullvad.mullvadvpn", ["net.mullvad.mullvadvpn.ui.MainActivity"]),
    ("key", "com.x8bit.bitwarden", ["com.x8bit.bitwarden.MainActivity"]),
    ("key", "proton.android.pass", [".ui.MainActivity"]),
    ("key", "com.keepassdroid", ["com.keepassdroid.fileselect.FileSelectActivity"]),
    ("key", "com.kunzisoft.keepass.libre", ["com.kunzisoft.keepass.activities.FileDatabaseSelectActivity"]),
    ("auth", "com.azure.authenticator", ["com.azure.authenticator.MainActivity"]),
    ("auth", "com.google.android.apps.authenticator2", ["com.google.android.apps.authenticator.AuthenticatorActivity"]),
    ("auth", "com.beemdevelopment.aegis", ["com.beemdevelopment.aegis.ui.MainActivity"]),
    ("auth", "org.shadowice.flocke.andotp", ["org.shadowice.flocke.andotp.Activities.MainActivity"]),

    # ---- Productivity ----
    ("mail", "com.microsoft.office.outlook", ["com.microsoft.office.outlook.MainActivity"]),
    ("mail", "ch.protonmail.android", ["ch.protonmail.android.activities.SplashActivity"]),
    ("mail", "me.proton.android.mail", [".MainActivity"]),
    ("mail", "com.fsck.k9", ["com.fsck.k9.activity.Accounts"]),
    ("mail", "eu.faircode.email", ["eu.faircode.email.ActivityMain"]),
    ("doc", "com.microsoft.office.word", ["com.microsoft.office.word.WordActivity"]),
    ("sheet", "com.microsoft.office.excel", ["com.microsoft.office.excel.ExcelActivity"]),
    ("slides", "com.microsoft.office.powerpoint", ["com.microsoft.office.powerpoint.PPTActivity"]),
    ("pdf", "com.adobe.reader", ["com.adobe.reader.AdobeReader"]),
    ("notes", "md.obsidian", [".MainActivity"]),
    ("notes", "com.todoist", ["com.todoist.activity.HomeActivity"]),
    ("notes", "notion.id", ["notion.id.MainActivity"]),
    ("notes", "com.nononsenseapps.notepad", [".ActivityMain"]),
    ("book", "org.readera", ["org.readera.MainActivity"]),
    ("book", "com.amazon.kindle", ["com.amazon.kindle.UpgradePage"]),

    # ---- Travel / shopping ----
    ("shopping", "com.amazon.mShop.android.shopping", ["com.amazon.mShop.home.HomeActivity"]),
    ("maps", "com.ubercab", ["com.ubercab.presidio.app.core.root.RootActivity"]),
    ("shopping", "com.ubercab.eats", ["com.ubercab.eats.app.feature.home.EatsHomeActivity"]),
    ("maps", "com.airbnb.android", ["com.airbnb.android.feat.legacy.MainActivity"]),
    ("compass", "com.google.android.apps.maps.compass", [".CompassActivity"]),

    # ---- Misc system / OEM ----
    ("flashlight", "com.android.systemui.flashlight", [".FlashlightActivity"]),
    ("settings", "com.android.settings.intelligence", [".search.SearchActivity"]),
]

# Nova/Lawnchair keyword fallbacks for unmatched stock apps
KEYWORDS = [
    (":PHONE", "phone"), (":SMS", "messages"), (":BROWSER", "browser"),
    (":EMAIL", "mail"), (":CAMERA", "camera"), (":CALENDAR", "calendar"),
    (":CLOCK", "clock"), (":GALLERY", "photos"), (":CONTACTS", "contacts"),
    (":MUSIC", "music"), (":MARKET", "store"), (":SETTINGS", "settings"),
]


def build():
    RES.mkdir(parents=True, exist_ok=True)

    # appfilter.xml
    af = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>",
          "    <!-- OneQode icon pack - component map. Generated by tools/appfilter.py -->",
          "    <!-- iconback gives UNMATCHED apps an on-brand glass backplate (Nova/Apex;",
          "         Lawnchair ignores this and falls back to themed/original icons). -->",
          '    <iconback img1="iconback"/>',
          '    <scale factor="0.86"/>', ""]
    seen = set()
    pkg_glyph = OrderedDict()
    for glyph, pkg, acts in MAP:
        pkg_glyph.setdefault(pkg, glyph)
        for act in acts:
            comp = act if act.startswith(".") and False else act
            # build full component; activities starting with "." are relative to pkg
            full_act = (pkg + act) if act.startswith(".") else act
            key = f"{pkg}/{full_act}"
            if key in seen:
                continue
            seen.add(key)
            af.append(f'    <item component="ComponentInfo{{{pkg}/{full_act}}}" drawable="ic_{glyph}"/>')
    af.append("")
    for kw, glyph in KEYWORDS:
        af.append(f'    <item component="{kw}" drawable="ic_{glyph}"/>')
    af.append("</resources>")
    (RES / "appfilter.xml").write_text("\n".join(af) + "\n")

    # grayscale_icon_map.xml (Lawnchair themed icons, per-package)
    gm = ['<?xml version="1.0" encoding="utf-8"?>', "<icons>",
          "    <!-- OneQode themed (monochrome) icons for Lawnchair -->"]
    for pkg, glyph in pkg_glyph.items():
        gm.append(f'    <icon package="{pkg}" drawable="@drawable/ic_{glyph}_mono"/>')
    gm.append("</icons>")
    (RES / "grayscale_icon_map.xml").write_text("\n".join(gm) + "\n")

    # drawable.xml (manual picker catalogue)
    glyphs = sorted({g for g, _, _ in MAP})
    dx = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>",
          '    <category title="OneQode"/>']
    for g in glyphs:
        dx.append(f'    <item drawable="ic_{g}"/>')
    dx.append("</resources>")
    (RES / "drawable.xml").write_text("\n".join(dx) + "\n")

    print(f"appfilter.xml: {len(seen)} components + {len(KEYWORDS)} keywords")
    print(f"grayscale_icon_map.xml: {len(pkg_glyph)} packages")
    print(f"drawable.xml: {len(glyphs)} glyphs catalogued")


if __name__ == "__main__":
    build()
