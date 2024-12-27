import sqlite3
from dataclasses import asdict
from pathlib import Path

from groundanchor import GroundAnchor


def save_to_sqlite(db_file: Path, anchors: set[GroundAnchor]):
    # Verbindung herstellen
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Tabelle erstellen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ground_anchors (
            pid TEXT PRIMARY KEY,
            lat REAL,
            lon REAL,
            alt REAL,
            hgt REAL
        )
    """)

    # Daten einfügen
    for anchor in anchors:
        cursor.execute(
            """
            INSERT OR REPLACE INTO ground_anchors (pid, lat, lon, alt, hgt)
            VALUES (:pid, :lat, :lon, :alt, :hgt)
        """,
            asdict(anchor),
        )

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()


def load_from_sqlite(db_file: str) -> set[GroundAnchor]:
    # Verbindung herstellen
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Daten abrufen
    try:
        cursor.execute("SELECT pid, lat, lon, alt, hgt FROM ground_anchors")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        return set()
    finally:
        conn.close()

    # Liste von GroundAnchor-Objekten erstellen
    anchors = [GroundAnchor(*row) for row in rows]
    return set(anchors)


# Beispiel
# save_to_sqlite("anchors.db", cached_anchors)
# loaded_anchors = load_from_sqlite("anchors.db")
# print(loaded_anchors)
