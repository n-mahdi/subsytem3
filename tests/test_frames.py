import os
from datetime import datetime, timedelta, timezone

from alert_engine.frames import FolderFrameSource

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def write_frame(folder, camera_id="cam-01", age_s=0.0):
    path = folder / f"{camera_id}.jpg"
    path.write_bytes(b"jpeg-bytes")
    stamp = (NOW - timedelta(seconds=age_s)).timestamp()
    os.utime(path, (stamp, stamp))
    return path


def test_returns_recent_frame(tmp_path):
    write_frame(tmp_path, age_s=1.0)
    assert FolderFrameSource(tmp_path, max_age_s=5).get_frame("cam-01", NOW) == b"jpeg-bytes"


def test_stale_frame_is_not_used(tmp_path):
    write_frame(tmp_path, age_s=30.0)
    assert FolderFrameSource(tmp_path, max_age_s=5).get_frame("cam-01", NOW) is None


def test_missing_frame_returns_none(tmp_path):
    assert FolderFrameSource(tmp_path, max_age_s=5).get_frame("cam-01", NOW) is None


def test_camera_id_cannot_escape_frame_folder(tmp_path):
    frames = tmp_path / "frames"
    frames.mkdir()
    write_frame(tmp_path, camera_id="secret")
    assert FolderFrameSource(frames, max_age_s=5).get_frame("../secret", NOW) is None
