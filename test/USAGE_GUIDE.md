# Quick Usage Guide - Edge-Based Plate Straightener

## 🚀 Fastest Way to Test

**Double-click this file:**
```
test_straightener.bat
```

Done! A window will open showing your screenshot before and after straightening.

---

## 📝 Three Simple Methods

### Method 1: Your Screenshot (Easiest)

```batch
test_straightener.bat
```

Tests with: `C:\Users\maazs\Pictures\Screenshots\Screenshot 2026-01-06 010749.png`

### Method 2: Specific Snapshot

```batch
test_with_snapshot.bat MH20EJ0364_20260106_010636.jpg
```

Or drag and drop any image onto `test_with_snapshot.bat`

### Method 3: Multiple Snapshots

```batch
batch_test_snapshots.bat
```

Tests all `MH*.jpg` files in the snapshots folder

---

## 💻 Command Line

### Basic Usage

```cmd
conda activate alpr_dev
cd test
python demo_straightener.py "../snapshots/your_image.jpg"
```

### With Your Screenshot

```cmd
conda activate alpr_dev
cd test
python demo_straightener.py "C:\Users\maazs\Pictures\Screenshots\Screenshot 2026-01-06 010749.png"
```

### Test Any Image

```cmd
conda activate alpr_dev
cd test
python demo_straightener.py "C:\path\to\any\image.jpg"
```

---

## 📊 What You'll See

### Window Display (3 Panels)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌──────────┐  │  ┌──────────┐  │  ┌──────────┐         │
│  │ ORIGINAL │  │  │STRAIGHT  │  │  │  EDGES   │         │
│  │  (tilt)  │  │  │ (fixed)  │  │  │ (debug)  │         │
│  └──────────┘  │  └──────────┘  │  └──────────┘         │
│                                                         │
│   Shows the       Straightened      Green lines         │
│   cropped         result with       show detected       │
│   plate with      alignment         horizontal          │
│   detected                           edges              │
│   angle                                                 │
└─────────────────────────────────────────────────────────┘
```

**Press any key** in the window to close it.

### Console Output

```
[OK] Loading image: ...
  Image size: (120, 350, 3)

[OK] Creating PlateStraightener instance...
[OK] Detecting edges and calculating angle...

----------------------------------------------------------------------
Processing...
----------------------------------------------------------------------
[WARNING] Plate is tilted by 12.45 degrees - straightening...

[OK] Displaying results...

============================================================
PLATE STRAIGHTENING RESULTS (EDGE-BASED)
============================================================
Original size:      (120, 350, 3)
Detected angle:     12.45 degrees
Needs correction:   True
Method used:        straightened
Straightened size:  (135, 365, 3)
============================================================

[OK] Saved straightened image to: test\image_straightened.jpg
[OK] Demo complete!
```

---

## 📁 Output Files

Straightened images are automatically saved as:

**Original**: `MH20EJ0364_20260106_010636.jpg`  
**Output**: `MH20EJ0364_20260106_010636_straightened.jpg`

Saved in the `test\` folder.

---

## ⚙️ Configuration

### Change Angle Threshold

Edit `demo_straightener.py` line 46:

```python
# More aggressive (straighten slight tilts)
straightener = PlateStraightener(min_angle_threshold=0.5)

# Default (balanced)
straightener = PlateStraightener(min_angle_threshold=1.0)

# Conservative (only major tilts)
straightener = PlateStraightener(min_angle_threshold=2.0)
```

### Change Test Image

Edit `test_straightener.bat` line 14:

```batch
python demo_straightener.py "path\to\your\image.jpg"
```

---

## 🔧 Integration with Your ALPR System

### Where to Add It

In `alpr_engine.py`, add AFTER YOLO detection but BEFORE preprocessing:

```python
def process_frame(self, frame: np.ndarray) -> Optional[dict]:
    # Detect plate with YOLO
    detection = self.detect_plate(frame)
    if detection is None:
        return None
    
    plate_img, det_confidence = detection
    
    # ✨ ADD THIS: Straighten the cropped plate
    from test.plate_straightener import PlateStraightener
    straightener = PlateStraightener(min_angle_threshold=1.0)
    plate_img, angle, debug = straightener.process(plate_img)
    
    # Continue with preprocessing and OCR
    ocr_result = self.read_plate_text(plate_img)
    # ... rest of code
```

### Testing Integration

1. Add the code above
2. Run your ALPR system
3. Check console for: `[WARNING] Plate is tilted by X degrees - straightening...`
4. Compare OCR accuracy before and after

---

## 🐛 Troubleshooting

### "conda is not recognized"

**Open Anaconda Prompt instead:**
1. Start Menu → Anaconda Prompt
2. `cd C:\Users\maazs\Documents\Projects\ALPR_TollPlaza_System\test`
3. `python demo_straightener.py "path\to\image.jpg"`

### "File not found"

**Check the path:**
- Use absolute paths: `C:\full\path\to\image.jpg`
- Or relative from test folder: `../snapshots/image.jpg`
- Use double backslashes: `C:\\path\\image.jpg`

### Window doesn't appear

**Try:**
1. Check console for errors
2. Make sure image loaded successfully
3. Look for the window behind other windows
4. Try Alt+Tab to find it

### No edges detected (angle = 0.00)

**This is normal if:**
- Plate is already straight
- Image is too blurry
- Module will use fallback contour method

**Solution**: Check the right panel for detected edges

### Wrong angle detected

**Check the debug panel (right):**
- Green lines show detected edges
- If lines are wrong, image might be too noisy
- Try preprocessing first or adjust Canny thresholds

---

## 📷 Testing with Different Image Types

### Works Best With:
- ✅ Cropped license plate images
- ✅ Clear plate boundaries
- ✅ Good contrast
- ✅ Minimal blur

### May Need Adjustment:
- ⚠️ Very blurry images
- ⚠️ Low contrast
- ⚠️ Partial plates
- ⚠️ Heavy shadows

### Test Images

Try these from your snapshots:
```batch
test_with_snapshot.bat MH20EJ0364_20260106_010636.jpg
test_with_snapshot.bat DL7CQ1939_20260106_010419.jpg
test_with_snapshot.bat TN09BY9726_20260106_010558.jpg
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Test your screenshot | `test_straightener.bat` |
| Test a snapshot | `test_with_snapshot.bat name.jpg` |
| Test multiple | `batch_test_snapshots.bat` |
| Manual test | `python demo_straightener.py "path\to\image.jpg"` |
| Change threshold | Edit line 46 in `demo_straightener.py` |
| View saved output | Check `test\` folder for `*_straightened.jpg` |

---

## ✅ What This Module Does

1. **Input**: Takes cropped license plate from YOLO
2. **Detect**: Finds top/bottom edges using Canny + Hough
3. **Calculate**: Determines tilt angle from horizontal edges
4. **Straighten**: Rotates plate to align horizontally
5. **Crop**: Removes excess white borders
6. **Display**: Shows before/after/edges comparison
7. **Save**: Outputs straightened image

---

## 🎓 Understanding the Output

### Detected Angle

- **0-2°**: Plate is already straight (no correction needed)
- **2-5°**: Slight tilt (minor correction)
- **5-10°**: Moderate tilt (noticeable improvement)
- **10-20°**: Significant tilt (major correction)
- **>20°**: Severe tilt (substantial improvement)

### Debug Panel (Right Side)

**Green Lines** = Detected horizontal edges
- More lines = better detection
- Parallel lines = consistent angle
- Few/no lines = fallback to contour method

---

## 📖 More Information

- **Technical Details**: See `README.md`
- **Algorithm**: See `plate_straightener.py` (well-commented)
- **Examples**: See output files with `_straightened.jpg` suffix

---

**Ready to go!** Just double-click `test_straightener.bat` 🚀
