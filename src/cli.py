"""
Command Line Interface for 2D to 3D Converter
"""
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Main CLI entry point"""
    from src.version import __version__, get_version_string
    from src.utils.logger import setup_logger
    
    parser = argparse.ArgumentParser(
        description="2D to 3D SBS Converter - AI-powered video conversion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single image
  %(prog)s convert input.jpg -o output_sbs.jpg
  
  # Convert video with custom parameters
  %(prog)s convert movie.mp4 -o movie_sbs.mp4 --depth 75 --ipd 65
  
  # Batch convert folder
  %(prog)s batch ./videos/ -o ./output/ --format half_sbs
  
  # Show system info
  %(prog)s info
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {get_version_string()}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert single file')
    convert_parser.add_argument('input', type=str, help='Input file path')
    convert_parser.add_argument('-o', '--output', type=str, required=True,
                               help='Output file path')
    convert_parser.add_argument('--depth', type=int, default=75,
                               help='Depth intensity (0-100, default: 75)')
    convert_parser.add_argument('--ipd', type=int, default=65,
                               help='Interpupillary distance in mm (default: 65)')
    convert_parser.add_argument('--convergence', type=float, default=1.0,
                               help='Convergence distance (default: 1.0)')
    convert_parser.add_argument('--format', type=str, default='half_sbs',
                               choices=['half_sbs', 'full_sbs', 'top_bottom', 'anaglyph'],
                               help='Output format (default: half_sbs)')
    convert_parser.add_argument('--quality', type=str, default='balanced',
                               choices=['fast', 'balanced', 'high'],
                               help='Quality preset (default: balanced)')
    convert_parser.add_argument('--model', type=str, default='midas_v3',
                               choices=['midas_v3', 'depth_anything_v2'],
                               help='Depth estimation model (default: midas_v3)')
    convert_parser.add_argument('--gpu', type=int, default=0,
                               help='GPU device ID (default: 0, use -1 for CPU)')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch convert folder')
    batch_parser.add_argument('input_dir', type=str, help='Input directory')
    batch_parser.add_argument('-o', '--output_dir', type=str, required=True,
                             help='Output directory')
    batch_parser.add_argument('--pattern', type=str, default='*.mp4',
                             help='File pattern (default: *.mp4)')
    batch_parser.add_argument('--depth', type=int, default=75,
                             help='Depth intensity (0-100)')
    batch_parser.add_argument('--format', type=str, default='half_sbs',
                             choices=['half_sbs', 'full_sbs', 'top_bottom'],
                             help='Output format')
    batch_parser.add_argument('--quality', type=str, default='balanced',
                             choices=['fast', 'balanced', 'high'],
                             help='Quality preset')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show system information')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview single frame')
    preview_parser.add_argument('input', type=str, help='Input file')
    preview_parser.add_argument('--frame', type=int, default=0,
                               help='Frame number for video (default: 0)')
    preview_parser.add_argument('--depth', type=int, default=75,
                               help='Depth intensity')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logger
    logger = setup_logger(console_level='INFO')
    
    # Execute command
    if args.command == 'convert':
        from src.cli_commands import convert_file
        return convert_file(args, logger)
    
    elif args.command == 'batch':
        from src.cli_commands import batch_convert
        return batch_convert(args, logger)
    
    elif args.command == 'info':
        from src.cli_commands import show_info
        return show_info(logger)
    
    elif args.command == 'preview':
        from src.cli_commands import preview_frame
        return preview_frame(args, logger)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
