package com.oneqode.theme;

/**
 * Sunrise/sunset calculation (NOAA-style "sunrise equation"). Pure math, no
 * network or location services. Longitude is EAST-positive.
 */
public final class SolarClock {

    private static final double RAD = Math.PI / 180.0;
    private static final long DAY_MS = 86_400_000L;
    private static final double UNIX_EPOCH_JD = 2440587.5;

    private SolarClock() {}

    /** Result: sunrise/sunset epoch millis. Either may be Long.MIN/MAX on polar day/night. */
    public static final class Times {
        public final long sunrise, sunset;
        public final boolean polar;
        Times(long r, long s, boolean p) { sunrise = r; sunset = s; polar = p; }
    }

    /** Compute sunrise/sunset for the solar day containing baseMillis + dayOffset days. */
    public static Times compute(double lat, double lng, long baseMillis, int dayOffset) {
        long t = baseMillis + (long) dayOffset * DAY_MS;
        double jdate = (double) t / DAY_MS + UNIX_EPOCH_JD;

        double lw = -lng; // west-positive in the formula
        double n = Math.round(jdate - 2451545.0 + 0.0008);
        double jStar = n + lw / 360.0;

        double m = mod360(357.5291 + 0.98560028 * jStar);
        double c = 1.9148 * Math.sin(m * RAD)
                 + 0.0200 * Math.sin(2 * m * RAD)
                 + 0.0003 * Math.sin(3 * m * RAD);
        double lambda = mod360(m + c + 180 + 102.9372);
        double jTransit = 2451545.0 + jStar + 0.0053 * Math.sin(m * RAD)
                        - 0.0069 * Math.sin(2 * lambda * RAD);

        double delta = Math.asin(Math.sin(lambda * RAD) * Math.sin(23.4397 * RAD));
        double cosOmega = (Math.sin(-0.833 * RAD) - Math.sin(lat * RAD) * Math.sin(delta))
                        / (Math.cos(lat * RAD) * Math.cos(delta));

        if (cosOmega < -1.0) return new Times(Long.MIN_VALUE, Long.MAX_VALUE, true); // polar day
        if (cosOmega > 1.0)  return new Times(Long.MAX_VALUE, Long.MIN_VALUE, true); // polar night

        double omega = Math.acos(cosOmega) / RAD; // degrees
        double jRise = jTransit - omega / 360.0;
        double jSet  = jTransit + omega / 360.0;
        return new Times(julianToMillis(jRise), julianToMillis(jSet), false);
    }

    private static long julianToMillis(double jd) {
        return (long) ((jd - UNIX_EPOCH_JD) * DAY_MS);
    }

    private static double mod360(double x) {
        x %= 360.0;
        return x < 0 ? x + 360.0 : x;
    }

    /**
     * Given now, decide the next switch: returns {nextBoundaryMillis, isDayAfter}.
     * isDayAfter == 1 means it becomes day at that boundary (sunrise), 0 means night.
     */
    public static long[] nextBoundary(double lat, double lng, long now) {
        Times today = compute(lat, lng, now, 0);
        if (today.polar) {
            // No sunrise/sunset today: switch at local midnight, pick by daylight side.
            boolean isDay = today.sunrise == Long.MIN_VALUE && today.sunset == Long.MAX_VALUE;
            long nextMidnight = now - (now % DAY_MS) + DAY_MS;
            return new long[] { nextMidnight, isDay ? 1 : 0 };
        }
        if (now < today.sunrise) return new long[] { today.sunrise, 1 };
        if (now < today.sunset)  return new long[] { today.sunset, 0 };
        Times tomorrow = compute(lat, lng, now, 1);
        long r = tomorrow.polar ? (now - (now % DAY_MS) + DAY_MS) : tomorrow.sunrise;
        return new long[] { r, 1 };
    }

    /** Is it currently daytime at this location? */
    public static boolean isDay(double lat, double lng, long now) {
        Times t = compute(lat, lng, now, 0);
        if (t.polar) return t.sunrise == Long.MIN_VALUE && t.sunset == Long.MAX_VALUE;
        return now >= t.sunrise && now < t.sunset;
    }
}
