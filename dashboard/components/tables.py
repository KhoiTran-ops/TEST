"""Table presentation helpers."""
def display_frame(frame):
    return frame.drop(columns=[c for c in ["id", "created_at"] if c in frame], errors="ignore")
