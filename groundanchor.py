from dataclasses import dataclass
from typing import Any


@dataclass
class GroundAnchor:
    """
    A class to represent a ground anchor with specific geographical coordinates and height.

    Attributes:
    -----------
    pid : str
        The unique identifier for the ground anchor.
    lat : float
        The latitude of the ground anchor.
    lon : float
        The longitude of the ground anchor.
    alt : float
        The altitude of the ground anchor.
    hgt : float
        The height of the ground anchor.

    Methods:
    --------
    __eq__(other: object) -> bool
        Checks if another object is equal to this GroundAnchor based on the pid attribute.

    __hash__() -> int
        Returns the hash value of the GroundAnchor based on the pid attribute.
    """

    pid: str
    lat: float
    lon: float
    alt: float
    hgt: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GroundAnchor):
            return False
        return self.pid == other.pid

    def __hash__(self) -> int:
        return hash(self.pid)


all_anchors = list[tuple[GroundAnchor | None, GroundAnchor | None]]


def merge_anchors(
    current_anchors: list[GroundAnchor], cached_anchors: set[GroundAnchor]
) -> list[tuple[GroundAnchor | None, GroundAnchor | None]]:
    """
    Merges the current and cached ground anchors into a single list of tuples.

    Parameters:
    -----------
    current_anchors : list[GroundAnchor]
        The list of current ground anchors.
    cached_anchors : set[GroundAnchor]
        The set of cached ground anchors.

    Returns:
    --------
    list[tuple[GroundAnchor | None, GroundAnchor | None]]
        A list of tuples, where each tuple contains a current anchor and a cached anchor.
        If an anchor is not found in the current or cached list, the corresponding tuple element will be None.
    """
    current_dict = {anchor.pid: anchor for anchor in current_anchors}
    cached_dict = {anchor.pid: anchor for anchor in cached_anchors}

    all_pids = set(current_dict.keys()) | set(cached_dict.keys())

    result = [(current_dict.get(pid), cached_dict.get(pid)) for pid in all_pids]

    return result


def extract_anchors(savefile: dict[str, Any]) -> list[GroundAnchor]:
    """
    Extracts ground anchors from a game save file.

    This function parses the savefile dictionary to find and create GroundAnchor objects
    for all vessels that are Stamp-O-Tron Ground Anchors and deployed ground parts.

    Parameters:
    -----------
    savefile : dict[str, Any]
        A dictionary representing the game save file structure. It should contain
        a nested structure with GAME -> FLIGHTSTATE -> VESSEL containing vessel data.

    Returns:
    --------
    list[GroundAnchor]
        A list of GroundAnchor objects extracted from the savefile. Each GroundAnchor
        represents a deployed Stamp-O-Tron Ground Anchor with its properties (pid, lat, lon, alt, hgt).
    """
    vessels: dict[str, Any] = savefile["GAME"]["FLIGHTSTATE"]["VESSEL"]
    anchors: list[GroundAnchor] = []

    for vessel in vessels:
        if vessel["name"] != "Stamp-O-Tron Ground Anchor":  # type: ignore
            continue

        if vessel["type"] == "DeployedGroundPart":  # type: ignore
            anchors.append(
                GroundAnchor(
                    pid=vessel["pid"],  # type: ignore
                    lat=float(vessel["lat"]),  # type: ignore
                    lon=float(vessel["lon"]),  # type: ignore
                    alt=float(vessel["alt"]),  # type: ignore
                    hgt=float(vessel["hgt"]),  # type: ignore
                )
            )

    return anchors


def value_changed(value_1: float, value_2: float) -> bool:
    """
    Compare two float values to determine if they have changed, considering rounding to 3 decimal places.

    Parameters:
    -----------
    value_1 : float
        The first float value to compare.
    value_2 : float
        The second float value to compare.

    Returns:
    --------
    bool
        True if the rounded values are different, False if they are the same.
    """
    return round(value_1, 3) != round(value_2, 3)


def inspect_anchors(
    anchors: all_anchors, stored_anchors: set[GroundAnchor]
) -> set[GroundAnchor]:
    """
    Inspect and compare current and cached ground anchors, updating stored anchors and identifying anchors
    that need restoration.

    This function iterates through pairs of current and cached anchors, updating the stored_anchors set
    and identifying anchors that have changed in altitude or height and need to be restored.

    Parameters:
    -----------
    anchors : all_anchors
        A list of tuples, where each tuple contains a current anchor and a cached anchor.
        Each anchor can be either a GroundAnchor object or None.
    stored_anchors : set[GroundAnchor]
        A set of GroundAnchor objects representing the currently stored anchors.

    Returns:
    --------
    set[GroundAnchor]
        A set of GroundAnchor objects that need to be restored due to changes in altitude or height.
    """
    anchors_to_restore: set[GroundAnchor] = set()

    for anchor in anchors:
        current_anchor = anchor[0]
        cached_anchor = anchor[1]

        if cached_anchor is None and current_anchor is not None:
            stored_anchors.add(current_anchor)
            print(f"Added Stamp-O-Tron Ground Anchor {current_anchor.pid}")
            continue

        if current_anchor is None and cached_anchor is not None:
            continue

        if current_anchor is not None and cached_anchor is not None:
            if value_changed(current_anchor.lat, cached_anchor.lat) or value_changed(
                current_anchor.lon, cached_anchor.lon
            ):
                print("Position has changed")
                stored_anchors.discard(cached_anchor)
                stored_anchors.add(current_anchor)

            if value_changed(current_anchor.alt, cached_anchor.alt):
                anchors_to_restore.add(cached_anchor)
                print(
                    f"Altitude has changed: {cached_anchor.alt} -> {current_anchor.alt}"
                )
            if value_changed(current_anchor.hgt, cached_anchor.hgt):
                anchors_to_restore.add(cached_anchor)
                print(
                    f"Height has changed: {cached_anchor.hgt} -> {current_anchor.hgt}"
                )

    return anchors_to_restore


def restore_anchor(savefile: dict[str, Any], anchor: GroundAnchor) -> dict[str, Any]:
    """
    Restore a ground anchor's properties in the game save file.

    This function updates the latitude, longitude, altitude, and height of a specific
    ground anchor in the game save file based on the provided GroundAnchor object.

    Parameters:
    -----------
    savefile : dict[str, Any]
        A dictionary representing the game save file structure. It should contain
        a nested structure with GAME -> FLIGHTSTATE -> VESSEL containing vessel data.
    anchor : GroundAnchor
        The GroundAnchor object containing the properties to be restored.

    Returns:
    --------
    dict[str, Any]
        The updated savefile dictionary with the restored anchor properties.
    """
    for vessel in savefile["GAME"]["FLIGHTSTATE"]["VESSEL"]:
        if vessel["pid"] == anchor.pid:
            vessel["lat"] = str(anchor.lat)
            vessel["lon"] = str(anchor.lon)
            vessel["alt"] = str(anchor.alt)
            vessel["hgt"] = str(anchor.hgt)
            break

    return savefile
