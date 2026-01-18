#!/bin/bash
# Convert all .webp files to .png and move originals to old/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Create old directory if it doesn't exist
mkdir -p old

# Check for webp files
shopt -s nullglob
webp_files=(*.webp)

if [ ${#webp_files[@]} -eq 0 ]; then
    echo "No .webp files found."
    exit 0
fi

echo "Found ${#webp_files[@]} .webp files to convert."

# Check for conversion tool
if command -v convert &>/dev/null; then
    CONVERTER="imagemagick"
elif command -v dwebp &>/dev/null; then
    CONVERTER="dwebp"
else
    echo "Error: Neither ImageMagick (convert) nor libwebp (dwebp) found."
    echo "Install with: sudo apt install imagemagick  OR  sudo apt install webp"
    exit 1
fi

echo "Using: $CONVERTER"

success=0
failed=0

for webp in "${webp_files[@]}"; do
    base="${webp%.webp}"
    png="${base}.png"

    echo -n "Converting $webp -> $png ... "

    if [ "$CONVERTER" = "imagemagick" ]; then
        if convert "$webp" "$png" 2>/dev/null; then
            mv "$webp" old/
            echo "done"
            ((success++))
        else
            echo "FAILED"
            ((failed++))
        fi
    else
        if dwebp "$webp" -o "$png" 2>/dev/null; then
            mv "$webp" old/
            echo "done"
            ((success++))
        else
            echo "FAILED"
            ((failed++))
        fi
    fi
done

echo ""
echo "Conversion complete: $success succeeded, $failed failed"
echo "Original .webp files moved to: $SCRIPT_DIR/old/"
