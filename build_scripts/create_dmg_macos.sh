#!/bin/bash
# Create macOS .dmg installer with drag-to-Applications

set -e  # Exit on error

echo "=================================="
echo "macOS DMG Installer Creator"
echo "=================================="
echo ""

# Variables
APP_NAME="2D to 3D Converter"
DMG_NAME="2D-to-3D-Converter-v1.0-macOS"
SOURCE_APP="dist/2D-to-3D-Converter.app"
DMG_DIR="dmg_temp"
FINAL_DMG="dist/$DMG_NAME.dmg"

# Check if app exists
if [ ! -d "$SOURCE_APP" ]; then
    echo "❌ Error: $SOURCE_APP not found"
    echo "Run PyInstaller build first: python3 build_scripts/build.py"
    exit 1
fi

echo "✅ Found application bundle: $SOURCE_APP"
echo ""

# Create temporary directory for DMG contents
echo "📁 Creating temporary DMG directory..."
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Copy .app to temp directory
echo "📦 Copying application bundle..."
cp -R "$SOURCE_APP" "$DMG_DIR/"

# Create Applications symlink
echo "🔗 Creating Applications symlink..."
ln -s /Applications "$DMG_DIR/Applications"

# Create README
echo "📝 Creating README..."
cat > "$DMG_DIR/README.txt" << 'EOF'
2D to 3D Converter v1.0
========================

INSTALLATION:
1. Drag "2D to 3D Converter.app" to the Applications folder
2. Launch from Applications or Spotlight

FIRST RUN:
- The app will download AI models (~1.4GB) on first use
- This is a one-time download and takes 5-15 minutes
- Requires internet connection for initial setup

SYSTEM REQUIREMENTS:
- macOS 10.15 or later
- 8GB RAM minimum (16GB recommended)
- 5GB free disk space
- GPU recommended but not required

USAGE:
1. Drag & drop images or videos into the app
2. Adjust settings (depth, format, quality)
3. Click "Convert" to process
4. Find output in "converted" folder

SUPPORT:
- User Guide: Help → User Guide in app menu
- GitHub: [Your repository URL]
- Email: [Your support email]

LICENSE:
- Free for personal use
- Pro license available for commercial use
- See Help → About for details

Copyright © 2025 3D Conversion
EOF

echo "🎨 Setting up DMG layout..."

# Remove any existing DMG
rm -f "$FINAL_DMG"

# Create DMG
echo "💿 Creating disk image..."
echo "   This may take a few minutes..."

hdiutil create -volname "$APP_NAME" \
    -srcfolder "$DMG_DIR" \
    -ov \
    -format UDZO \
    -fs HFS+ \
    "$FINAL_DMG"

# Clean up temp directory
echo "🧹 Cleaning up..."
rm -rf "$DMG_DIR"

# Get DMG size
DMG_SIZE=$(du -h "$FINAL_DMG" | cut -f1)

echo ""
echo "=================================="
echo "✅ DMG Created Successfully!"
echo "=================================="
echo ""
echo "📦 Output: $FINAL_DMG"
echo "💾 Size: $DMG_SIZE"
echo ""
echo "🧪 TESTING:"
echo "   1. Double-click DMG to mount"
echo "   2. Drag app to Applications"
echo "   3. Eject DMG"
echo "   4. Launch from Applications"
echo ""
echo "📤 DISTRIBUTION:"
echo "   Upload to your download server/website"
echo "   Recommended: Code sign for better user experience"
echo ""

# Optional: Open in Finder
read -p "Open DMG in Finder? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open -R "$FINAL_DMG"
fi

echo "✅ Done!"
