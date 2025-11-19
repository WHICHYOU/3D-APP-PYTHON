#!/usr/bin/env python3
"""
Automated build script for 2D to 3D Converter
Handles building standalone executables for all platforms
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

class BuildManager:
    """Manages the build process for creating standalone executables"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.spec_file = self.root_dir / "build_config" / "2D-to-3D-Converter.spec"
        self.platform = platform.system().lower()
        
    def clean(self):
        """Remove previous build artifacts"""
        print("🧹 Cleaning previous build artifacts...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                print(f"  Removing {dir_path}")
                shutil.rmtree(dir_path)
        
        print("✅ Clean complete\n")
    
    def check_dependencies(self):
        """Verify all required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check PyInstaller - try to find it in common locations
        pyinstaller_cmd = shutil.which('pyinstaller')
        if not pyinstaller_cmd:
            home = Path.home()
            common_paths = [
                home / 'Library' / 'Python' / '3.9' / 'bin' / 'pyinstaller',
                home / '.local' / 'bin' / 'pyinstaller',
            ]
            for path in common_paths:
                if path.exists():
                    pyinstaller_cmd = str(path)
                    break
        
        if pyinstaller_cmd:
            try:
                result = subprocess.run(
                    [pyinstaller_cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"  ✅ PyInstaller ({result.stdout.strip()})")
                else:
                    print(f"  ❌ PyInstaller - Command failed")
                    return False
            except (subprocess.TimeoutExpired, Exception) as e:
                print(f"  ❌ PyInstaller - Error: {e}")
                return False
        else:
            print(f"  ❌ PyInstaller - NOT FOUND")
            print("     Install with: pip3 install pyinstaller")
            print("     May need to add ~/Library/Python/3.9/bin to PATH")
            return False
        
        # Check Python packages
        required_packages = [
            ('PyQt6', 'PyQt6'),
            ('torch', 'torch'),
            ('torchvision', 'torchvision'),
            ('opencv-python', 'cv2'),
            ('numpy', 'numpy'),
            ('timm', 'timm'),
        ]
        
        missing = []
        for display_name, import_name in required_packages:
            try:
                __import__(import_name)
                print(f"  ✅ {display_name}")
            except ImportError:
                print(f"  ❌ {display_name} - NOT FOUND")
                missing.append(display_name)
        
        if missing:
            print(f"\n❌ Missing packages: {', '.join(missing)}")
            print("Install with: pip3 install -r requirements-gui.txt")
            return False
        
        print("✅ All dependencies found\n")
        return True
    
    def check_resources(self):
        """Check if resource files exist, create placeholders if needed"""
        print("🎨 Checking resources...")
        
        resources_dir = self.root_dir / "resources"
        resources_dir.mkdir(exist_ok=True)
        
        # Check for icon files
        icon_files = {
            'darwin': resources_dir / 'app.icns',
            'windows': resources_dir / 'app.ico',
            'linux': resources_dir / 'app.png',
        }
        
        platform_icon = icon_files.get(self.platform)
        if platform_icon and not platform_icon.exists():
            print(f"  ⚠️  Missing icon: {platform_icon.name}")
            print(f"     Using default icon (create {platform_icon.name} for custom icon)")
        else:
            print(f"  ✅ Icon file found")
        
        print()
        return True
    
    def build(self, clean_first=True):
        """Build the standalone executable"""
        print(f"🏗️  Building for {self.platform}...\n")
        
        # Check everything is ready
        if not self.check_dependencies():
            return False
        
        if not self.check_resources():
            return False
        
        # Clean if requested
        if clean_first:
            self.clean()
        
        # Verify spec file exists
        if not self.spec_file.exists():
            print(f"❌ Spec file not found: {self.spec_file}")
            return False
        
        print(f"📝 Using spec file: {self.spec_file}")
        print(f"📁 Output directory: {self.dist_dir}\n")
        
        # Run PyInstaller
        print("🚀 Starting PyInstaller build...\n")
        
        # Find pyinstaller command - might be in user's Library/Python/bin
        pyinstaller_cmd = shutil.which('pyinstaller')
        if not pyinstaller_cmd:
            # Try common locations
            home = Path.home()
            common_paths = [
                home / 'Library' / 'Python' / '3.9' / 'bin' / 'pyinstaller',
                home / '.local' / 'bin' / 'pyinstaller',
            ]
            for path in common_paths:
                if path.exists():
                    pyinstaller_cmd = str(path)
                    break
        
        if not pyinstaller_cmd:
            print("❌ PyInstaller executable not found")
            return False
        
        print(f"Using: {pyinstaller_cmd}\n")
        
        try:
            result = subprocess.run(
                [pyinstaller_cmd, '--clean', str(self.spec_file)],
                cwd=str(self.root_dir),
                check=True,
                capture_output=False,
                text=True
            )
            
            print("\n✅ Build completed successfully!")
            self.show_build_info()
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Build failed with error code {e.returncode}")
            return False
        except FileNotFoundError:
            print("\n❌ PyInstaller not found. Install with: pip3 install pyinstaller")
            return False
    
    def show_build_info(self):
        """Display information about the built executable"""
        print("\n" + "="*60)
        print("📦 BUILD INFORMATION")
        print("="*60)
        
        if self.dist_dir.exists():
            items = list(self.dist_dir.iterdir())
            
            if items:
                print(f"\n📁 Output location: {self.dist_dir}")
                print("\n📄 Built files:")
                
                total_size = 0
                for item in items:
                    if item.is_file():
                        size = item.stat().st_size
                        size_mb = size / (1024 * 1024)
                        print(f"  • {item.name} ({size_mb:.1f} MB)")
                        total_size += size
                    elif item.is_dir():
                        # Calculate directory size
                        dir_size = sum(
                            f.stat().st_size 
                            for f in item.rglob('*') 
                            if f.is_file()
                        )
                        size_mb = dir_size / (1024 * 1024)
                        print(f"  • {item.name}/ ({size_mb:.1f} MB)")
                        total_size += dir_size
                
                total_mb = total_size / (1024 * 1024)
                print(f"\n💾 Total size: {total_mb:.1f} MB")
                
                # Platform-specific instructions
                print("\n" + "="*60)
                print("🚀 NEXT STEPS")
                print("="*60)
                
                if self.platform == 'darwin':
                    print("\nmacOS Build:")
                    print("  1. Find the .app bundle in dist/")
                    print("  2. Test: Double-click to launch")
                    print("  3. Sign (optional): codesign --force --deep --sign - 'dist/*.app'")
                    print("  4. Create DMG: build_scripts/create_dmg_macos.sh")
                    
                elif self.platform == 'windows':
                    print("\nWindows Build:")
                    print("  1. Find the .exe in dist/")
                    print("  2. Test: Double-click to launch")
                    print("  3. Sign (optional): signtool sign /f cert.pfx dist/*.exe")
                    print("  4. Create installer: build_scripts/create_installer_windows.bat")
                    
                else:  # Linux
                    print("\nLinux Build:")
                    print("  1. Find the executable in dist/")
                    print("  2. Test: ./dist/2D-to-3D-Converter")
                    print("  3. Create AppImage: build_scripts/create_appimage_linux.sh")
            else:
                print("\n⚠️  No files found in dist/ directory")
        else:
            print("\n⚠️  dist/ directory not created")
        
        print("\n" + "="*60 + "\n")
    
    def test_build(self):
        """Test the built executable"""
        print("🧪 Testing built executable...\n")
        
        if self.platform == 'darwin':
            # macOS: Find .app bundle
            app_bundles = list(self.dist_dir.glob('*.app'))
            if app_bundles:
                app_path = app_bundles[0]
                exe_path = app_path / 'Contents' / 'MacOS' / '2D to 3D Converter'
                print(f"Found app bundle: {app_path.name}")
            else:
                print("❌ No .app bundle found")
                return False
        else:
            # Windows/Linux: Find executable
            exe_name = '2D-to-3D-Converter.exe' if self.platform == 'windows' else '2D-to-3D-Converter'
            exe_path = self.dist_dir / exe_name
        
        if not exe_path.exists():
            print(f"❌ Executable not found: {exe_path}")
            return False
        
        print(f"✅ Executable found: {exe_path}")
        print("\n⚠️  Manual testing required:")
        print(f"   Run: {exe_path}")
        print("   Verify: Application launches and UI displays correctly")
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Build standalone executable for 2D to 3D Converter'
    )
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Skip cleaning previous build artifacts'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test the built executable after building'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*60)
    print("2D TO 3D CONVERTER - BUILD SCRIPT")
    print("="*60 + "\n")
    
    # Create build manager and build
    builder = BuildManager()
    success = builder.build(clean_first=not args.no_clean)
    
    # Test if requested and build succeeded
    if success and args.test:
        builder.test_build()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
