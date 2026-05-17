"""
Market Scanner – sendet Long/Short-Signale per Telegram.

Konfiguration: Trage BOT_TOKEN und CHAT_ID in den Abschnitt
"KONFIGURATION" ein, bevor du das Skript startest.
"""

import time
import logging
import requests
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------------------------
# KONFIGURATION – hier deine Werte eintragen
# ---------------------------------------------------------------------------

BOT_TOKEN = "DEIN_BOT_TOKEN_HIER"   # z. B. "7312345678:AAFxxxxxx"
CHAT_ID   = "DEINE_CHAT_ID_HIER"    # z. B. "123456789"

# Welche Symbole sollen überwacht werden?
WATCHLIST = [
    "AAPL",    # Apple
    "NVDA",    # Nvidia
    "^GDAXI",  # DAX
    "^GSPC",   # S&P 500
    "MSFT",    # Microsoft
    "TSLA",    # Tesla
]

INTERVAL       = "15m"   # Kerzen-Intervall: "5m", "15m", "1h", "1d"
SCAN_PERIOD    = "5d"    # Wie viele historische Daten laden (yfinance-Format)
SLEEP_SECONDS  = 900     # Wie oft scannen? 900 s = 15 Minuten

# RSI-Schwellen
RSI_OVERSOLD   = 30
RSI_OVERBOUGHT = 70

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# INDIKATOREN
# ---------------------------------------------------------------------------

def berechne_rsi(close: pd.Series, periode: int = 14) -> pd.Series:
    delta  = close.diff()
    gewinn = delta.clip(lower=0)
    verlust = (-delta).clip(lower=0)
    avg_gewinn = gewinn.ewm(com=periode - 1, min_periods=periode).mean()
    avg_verlust = verlust.ewm(com=periode - 1, min_periods=periode).mean()
    rs  = avg_gewinn / avg_verlust
    rsi = 100 - (100 / (1 + rs))
    return rsi


def berechne_macd(
    close: pd.Series,
    schnell: int = 12,
    langsam: int = 26,
    signal:  int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    ema_schnell  = close.ewm(span=schnell, adjust=False).mean()
    ema_langsam  = close.ewm(span=langsam, adjust=False).mean()
    macd_linie   = ema_schnell - ema_langsam
    signal_linie = macd_linie.ewm(span=signal, adjust=False).mean()
    histogramm   = macd_linie - signal_linie
    return macd_linie, signal_linie, histogramm

# ---------------------------------------------------------------------------
# SIGNAL-ERKENNUNG
# ---------------------------------------------------------------------------

def erkenne_signale(ticker: str) -> list[dict]:
    """
    Lädt Kursdaten für 'ticker' und gibt eine Liste erkannter Signale zurück.
    Jedes Signal ist ein Dict mit den Schlüsseln:
        ticker, signal_typ, kurs, grund
    """
    signale = []

    try:
        daten = yf.download(
            ticker,
            period=SCAN_PERIOD,
            interval=INTERVAL,
            progress=False,
            auto_adjust=True,
        )
    except Exception as exc:
        log.warning("Fehler beim Laden von %s: %s", ticker, exc)
        return signale

    if daten.empty or len(daten) < 30:
        log.warning("%s: zu wenige Datenpunkte (%d Kerzen)", ticker, len(daten))
        return signale

    close = daten["Close"].squeeze()

    # Indikatoren berechnen
    rsi          = berechne_rsi(close)
    macd, sig, _ = berechne_macd(close)

    # Letzte zwei Werte für Kreuzungs-Erkennung
    rsi_aktuell  = rsi.iloc[-1]
    kurs_aktuell = close.iloc[-1]

    macd_jetzt   = macd.iloc[-1]
    macd_vorher  = macd.iloc[-2]
    sig_jetzt    = sig.iloc[-1]
    sig_vorher   = sig.iloc[-2]

    macd_kreuzt_hoch  = (macd_vorher < sig_vorher) and (macd_jetzt >= sig_jetzt)
    macd_kreuzt_runter = (macd_vorher > sig_vorher) and (macd_jetzt <= sig_jetzt)

    # --- LONG-Signale ---
    if rsi_aktuell < RSI_OVERSOLD:
        signale.append({
            "ticker":     ticker,
            "signal_typ": "LONG",
            "kurs":       kurs_aktuell,
            "grund":      f"RSI bei {rsi_aktuell:.1f} (überverkauft < {RSI_OVERSOLD})",
        })

    if macd_kreuzt_hoch:
        signale.append({
            "ticker":     ticker,
            "signal_typ": "LONG",
            "kurs":       kurs_aktuell,
            "grund":      f"MACD kreuzt Signallinie nach OBEN (MACD {macd_jetzt:.4f})",
        })

    # --- SHORT-Signale ---
    if rsi_aktuell > RSI_OVERBOUGHT:
        signale.append({
            "ticker":     ticker,
            "signal_typ": "SHORT",
            "kurs":       kurs_aktuell,
            "grund":      f"RSI bei {rsi_aktuell:.1f} (überkauft > {RSI_OVERBOUGHT})",
        })

    if macd_kreuzt_runter:
        signale.append({
            "ticker":     ticker,
            "signal_typ": "SHORT",
            "kurs":       kurs_aktuell,
            "grund":      f"MACD kreuzt Signallinie nach UNTEN (MACD {macd_jetzt:.4f})",
        })

    return signale

# ---------------------------------------------------------------------------
# TELEGRAM
# ---------------------------------------------------------------------------

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def sende_telegram(signal: dict) -> None:
    emoji = "📈" if signal["signal_typ"] == "LONG" else "📉"
    text = (
        f"{emoji} *{signal['signal_typ']}-Signal* – {signal['ticker']}\n"
        f"Kurs: *{signal['kurs']:.2f}*\n"
        f"Grund: {signal['grund']}\n"
        f"Intervall: {INTERVAL}"
    )
    payload = {
        "chat_id":    CHAT_ID,
        "text":       text,
        "parse_mode": "Markdown",
    }
    try:
        antwort = requests.post(TELEGRAM_URL, data=payload, timeout=10)
        antwort.raise_for_status()
        log.info("Telegram-Nachricht gesendet: %s %s", signal["signal_typ"], signal["ticker"])
    except requests.RequestException as exc:
        log.error("Telegram-Fehler: %s", exc)


def sende_start_nachricht() -> None:
    text = (
        "🤖 *Market Scanner gestartet*\n"
        f"Watchlist: {', '.join(WATCHLIST)}\n"
        f"Intervall: {INTERVAL} | Scan alle {SLEEP_SECONDS // 60} Min."
    )
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(TELEGRAM_URL, data=payload, timeout=10)
    except requests.RequestException as exc:
        log.warning("Start-Nachricht konnte nicht gesendet werden: %s", exc)

# ---------------------------------------------------------------------------
# HAUPTSCHLEIFE
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("Scanner gestartet. Watchlist: %s", WATCHLIST)
    sende_start_nachricht()

    while True:
        log.info("--- Neuer Scan-Durchlauf ---")
        for ticker in WATCHLIST:
            try:
                signale = erkenne_signale(ticker)
                for signal in signale:
                    log.info(
                        "Signal erkannt: %s %s | %s",
                        signal["signal_typ"],
                        signal["ticker"],
                        signal["grund"],
                    )
                    sende_telegram(signal)
                if not signale:
                    log.info("%s: kein Signal.", ticker)
            except Exception as exc:
                # Einzelne Ticker-Fehler sollen die Schleife nicht stoppen
                log.error("Unerwarteter Fehler bei %s: %s", ticker, exc)

        log.info("Warte %d Sekunden bis zum nächsten Scan ...", SLEEP_SECONDS)
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
