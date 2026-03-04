"""
Command-line argument parsing for scheduled and manual runs.
"""

import argparse
from typing import Optional


class CLIArgumentParser:
    """Parse command-line arguments for extraction bot."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all supported options."""
        parser = argparse.ArgumentParser(
            description='Medical Insurance Portal API Extraction Bot',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Interactive mode (default)
  python main.py
  
  # API mode with broker selection menu
  python main.py --mode=api
  
  # Scheduled run for all brokers (no prompts)
  python main.py --mode=api --brokers=all --scheduled
  
  # Run for specific brokers
  python main.py --mode=api --brokers=3,6
  
  # Standard extraction mode
  python main.py --mode=standard --brokers=3
            """
        )
        
        parser.add_argument(
            '--mode',
            type=str,
            choices=['standard', 'api'],
            default=None,
            help='Extraction mode: standard (database+census) or api (API-only)'
        )
        
        parser.add_argument(
            '--brokers',
            type=str,
            default=None,
            help='Broker selection: "all", single ID "3", or comma-separated "3,6"'
        )
        
        parser.add_argument(
            '--scheduled',
            action='store_true',
            help='Scheduled mode: bypass all confirmation prompts'
        )
        
        parser.add_argument(
            '--notify-failures-only',
            action='store_true',
            help='Send email notification only if extraction fails'
        )
        
        parser.add_argument(
            '--skip-upload',
            action='store_true',
            help='Extract data but skip database upload (testing mode)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable detailed logging output'
        )
        
        return parser
    
    def parse(self) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Returns:
            Namespace with parsed arguments
        """
        return self.parser.parse_args()
    
    def validate_args(self, args: argparse.Namespace) -> bool:
        """
        Validate argument combinations.
        
        Args:
            args: Parsed arguments
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Scheduled mode requires --mode and --brokers
        if args.scheduled:
            if not args.mode:
                raise ValueError("--scheduled requires --mode to be specified")
            if not args.brokers:
                raise ValueError("--scheduled requires --brokers to be specified")
        
        return True


def parse_cli_arguments() -> argparse.Namespace:
    """
    Parse and validate CLI arguments.
    
    Returns:
        Validated argument namespace
    """
    parser = CLIArgumentParser()
    args = parser.parse()
    parser.validate_args(args)
    return args
