import sqlite3
from typing import Optional

from groundanchor import GroundAnchor


class DatabaseHandler:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("db.sqlite3")
        self.cursor = self.conn.cursor()
        self._create_table()

    def __del__(self) -> None:
        self.conn.close()

    def _create_table(self) -> None:
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS ground_anchors ("
            "pid STRING PRIMARY KEY, "
            "deployed BOOLEAN, "
            "lat REAL, "
            "lon REAL, "
            "alt REAL, "
            "hgt REAL"
            ")"
        )
        self.conn.commit()

    def read(self) -> list[GroundAnchor]:
        data: list[GroundAnchor] = []
        self.cursor.execute("SELECT * FROM ground_anchors")
        for row in self.cursor.fetchall():
            data.append(GroundAnchor(*row))

        return data

    def get(self, uid: str) -> Optional[GroundAnchor]:
        self.cursor.execute("SELECT * FROM ground_anchors WHERE pid = ?", (uid,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return GroundAnchor(*row)

    def insert(self, anchor: GroundAnchor) -> None:
        self.cursor.execute(
            "INSERT INTO ground_anchors VALUES (?, ?, ?, ?, ?, ?)",
            (
                anchor.pid,
                anchor.deployed,
                anchor.lat,
                anchor.lon,
                anchor.alt,
                anchor.hgt,
            ),
        )
        self.conn.commit()

    def modify(self, anchor: GroundAnchor) -> None:
        self.cursor.execute(
            "UPDATE ground_anchors SET deployed = ?, lat = ?, lon = ?, alt = ?, hgt = ? WHERE pid = ?",
            (
                anchor.deployed,
                anchor.lat,
                anchor.lon,
                anchor.alt,
                anchor.hgt,
                anchor.pid,
            ),
        )
        self.conn.commit()

    def delete(self, uid: str) -> None:
        self.cursor.execute("DELETE FROM ground_anchors WHERE uid = ?", (uid,))
        self.conn.commit()
