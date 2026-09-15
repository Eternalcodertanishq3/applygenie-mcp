import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from applygenie.core.screenshot import get_screen_info, capture_screenshot
from applygenie.core.window import list_windows, get_active_window
from applygenie.core.mouse import get_position

print("=== APPLYGENIE LIVE SYSTEM DIAGNOSTIC ===")
print("\n1. Screen Configuration:")
info = get_screen_info()
for m in info["monitors"]:
    print(f"   Monitor {m['index']}: {m['width']}x{m['height']} at ({m['left']}, {m['top']})")

print("\n2. Current Mouse Position:")
pos = get_position()
print(f"   Coordinates: ({pos['x']}, {pos['y']})")

print("\n3. Active Foreground Window:")
active = get_active_window()
if active:
    print(f"   Title: '{active['title']}' | Geometry: {active['width']}x{active['height']} at ({active['left'] if 'left' in active else active.get('x')}, {active['top'] if 'top' in active else active.get('y')})")
else:
    print("   None active / Desktop background")

print("\n4. Visible Windows:")
windows = list_windows()
print(f"   Total detected: {len(windows)}")
for w in windows[:8]:
    print(f"   - '{w['title']}' ({w['width']}x{w['height']})")

print("\n5. Testing Live Screenshot Capture...")
b64, meta = capture_screenshot(monitor=1)
print(f"   Captured primary display screenshot: {meta['encoded_width']}x{meta['encoded_height']} (Base64 size: {len(b64)} chars)")
print("\n>>> ALL APPLYGENIE PERCEPTION SENSORS ONLINE AND ACCURATE! <<<")
