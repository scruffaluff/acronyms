"""Wait until frontend assets are ready for the backend server."""


from pathlib import Path
import time


# Frontend clears dist folder and rebuilds assets during each compile. There
# is a small time window where the assets exist before the frontend clears
# the dist folder. Sleeping for 1 second ensures the wait loop begins after
# the dist folder has been cleared.
time.sleep(1)
assets = Path(__file__).parents[1] / "dist/assets"

while not assets.exists():
    time.sleep(1)
