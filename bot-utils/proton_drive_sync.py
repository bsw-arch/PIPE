#!/usr/bin/env python3
"""
Proton Drive Sync for BSW-Arch Platform
Syncs documentation and specifications with Proton Drive (encrypted cloud storage)
Supports continuous monitoring and incremental updates to knowledge graph
FAGAM-compliant secure storage solution
"""

import argparse
import hashlib
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
except ImportError:
    print("ERROR: watchdog not installed. Install with: pip install watchdog")
    sys.exit(1)


class ProtonDriveSync:
    """Sync local documentation with Proton Drive"""

    def __init__(
        self,
        remote_path: str,
        local_path: Path,
        poll_interval: int = 60,
        auto_index: bool = True
    ):
        self.remote_path = remote_path
        self.local_path = Path(local_path)
        self.poll_interval = poll_interval
        self.auto_index = auto_index

        # Track file hashes to detect changes
        self.file_hashes: Dict[str, str] = {}

        # Indexer configuration
        self.indexer_script = Path("/opt/documentation/graph_indexer_with_specs.py")
        self.project_root = self.local_path

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"⚠️  Error hashing {file_path}: {e}")
            return ""

    def _is_proton_drive_mounted(self) -> bool:
        """Check if Proton Drive is mounted/accessible"""
        # This would check for the actual mount point or rclone remote
        # For now, we check if the remote path is specified
        return bool(self.remote_path)

    def _sync_from_remote(self) -> bool:
        """Pull changes from Proton Drive to local"""
        print(f"🔄 Syncing from Proton Drive: {self.remote_path} -> {self.local_path}")

        try:
            # Using rclone for Proton Drive sync
            # Install rclone first: curl https://rclone.org/install.sh | sudo bash
            # Configure: rclone config (add Proton Drive remote)

            result = subprocess.run([
                "rclone", "sync",
                f"{self.remote_path}",
                str(self.local_path),
                "--checksum",
                "--progress",
                "--exclude", ".git/**",
                "--exclude", "__pycache__/**",
                "--exclude", "*.pyc"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Sync from remote complete")
                return True
            else:
                print(f"❌ Sync failed: {result.stderr}")
                return False

        except FileNotFoundError:
            print("❌ rclone not found. Install with: curl https://rclone.org/install.sh | sudo bash")
            print("   Then configure: rclone config")
            return False
        except Exception as e:
            print(f"❌ Sync error: {e}")
            return False

    def _sync_to_remote(self) -> bool:
        """Push changes from local to Proton Drive"""
        print(f"🔄 Syncing to Proton Drive: {self.local_path} -> {self.remote_path}")

        try:
            result = subprocess.run([
                "rclone", "sync",
                str(self.local_path),
                f"{self.remote_path}",
                "--checksum",
                "--progress",
                "--exclude", ".git/**",
                "--exclude", "__pycache__/**",
                "--exclude", "*.pyc"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Sync to remote complete")
                return True
            else:
                print(f"❌ Sync failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Sync error: {e}")
            return False

    def _index_file(self, file_path: Path):
        """Index a single file into knowledge graph"""
        if not self.auto_index or not self.indexer_script.exists():
            return

        print(f"📊 Indexing: {file_path}")

        try:
            result = subprocess.run([
                "python3",
                str(self.indexer_script),
                str(file_path),
                "--incremental",
                "--project-root", str(self.project_root)
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Indexed: {file_path}")
            else:
                print(f"⚠️  Indexing warning: {result.stderr}")

        except Exception as e:
            print(f"❌ Indexing error: {e}")

    def _scan_changes(self) -> List[Path]:
        """Scan for changed files"""
        changed_files = []

        for file_path in self.local_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip ignored patterns
            if any(pattern in str(file_path) for pattern in [".git", "__pycache__", ".pyc"]):
                continue

            # Check if file has changed
            current_hash = self._get_file_hash(file_path)
            previous_hash = self.file_hashes.get(str(file_path))

            if current_hash and current_hash != previous_hash:
                changed_files.append(file_path)
                self.file_hashes[str(file_path)] = current_hash

        return changed_files

    def sync_once(self, direction: str = "pull"):
        """Perform a single sync operation"""
        if direction == "pull":
            if self._sync_from_remote():
                # Index changed files
                changed_files = self._scan_changes()
                for file_path in changed_files:
                    if file_path.suffix in [".py", ".yaml", ".yml", ".md"]:
                        self._index_file(file_path)
        elif direction == "push":
            self._sync_to_remote()
        elif direction == "both":
            self._sync_from_remote()
            self._sync_to_remote()

    def continuous_sync(self):
        """Run continuous bi-directional sync"""
        print(f"🔁 Starting continuous sync (polling every {self.poll_interval}s)")
        print(f"   Remote: {self.remote_path}")
        print(f"   Local:  {self.local_path}")
        print(f"   Auto-index: {self.auto_index}")
        print()
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Running sync cycle...")

                # Pull from remote
                if self._sync_from_remote():
                    # Check for changes and index
                    changed_files = self._scan_changes()
                    if changed_files:
                        print(f"📝 Found {len(changed_files)} changed files")
                        for file_path in changed_files:
                            if file_path.suffix in [".py", ".yaml", ".yml", ".md"]:
                                self._index_file(file_path)

                # Push to remote (in case of local changes)
                self._sync_to_remote()

                print(f"💤 Sleeping for {self.poll_interval}s...")
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n👋 Stopping continuous sync")


class FileChangeHandler(FileSystemEventHandler):
    """Handle file system events for real-time sync"""

    def __init__(self, sync: ProtonDriveSync):
        self.sync = sync
        self.last_sync = time.time()
        self.debounce_seconds = 5

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip ignored patterns
        if any(pattern in str(file_path) for pattern in [".git", "__pycache__", ".pyc"]):
            return

        print(f"🔄 File changed: {file_path}")

        # Debounce: wait before syncing
        current_time = time.time()
        if current_time - self.last_sync < self.debounce_seconds:
            return

        # Sync to remote
        self.sync._sync_to_remote()

        # Index if appropriate
        if file_path.suffix in [".py", ".yaml", ".yml", ".md"]:
            self.sync._index_file(file_path)

        self.last_sync = current_time

    def on_created(self, event):
        self.on_modified(event)


def watch_and_sync(sync: ProtonDriveSync):
    """Watch local directory and sync on changes"""
    print(f"👀 Watching directory: {sync.local_path}")
    print("   Changes will be synced to Proton Drive automatically")
    print("   Press Ctrl+C to stop")
    print()

    event_handler = FileChangeHandler(sync)
    observer = Observer()
    observer.schedule(event_handler, str(sync.local_path), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping file watcher")
        observer.stop()

    observer.join()


def setup_proton_drive():
    """Interactive setup for Proton Drive integration"""
    print("🔧 Proton Drive Setup for BSW-Arch Platform")
    print()
    print("This will configure rclone for Proton Drive access.")
    print()

    # Check if rclone is installed
    try:
        subprocess.run(["rclone", "version"], capture_output=True, check=True)
        print("✅ rclone is installed")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ rclone not found")
        print()
        print("Install rclone:")
        print("  curl https://rclone.org/install.sh | sudo bash")
        print()
        return

    print()
    print("Configure rclone for Proton Drive:")
    print("  1. Run: rclone config")
    print("  2. Select 'n' for new remote")
    print("  3. Name it 'protondrive'")
    print("  4. Select 'protondrive' from the list")
    print("  5. Follow authentication prompts")
    print()
    print("After configuration, you can use:")
    print("  Remote path format: protondrive:BSW-Arch/documentation")
    print()

    response = input("Open rclone config now? (y/n): ")
    if response.lower() == 'y':
        subprocess.run(["rclone", "config"])


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Proton Drive sync for BSW-Arch Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # One-time pull from Proton Drive
  %(prog)s pull protondrive:BSW-Arch/docs /opt/documentation

  # One-time push to Proton Drive
  %(prog)s push protondrive:BSW-Arch/docs /opt/documentation

  # Continuous bi-directional sync (polling)
  %(prog)s continuous protondrive:BSW-Arch/docs /opt/documentation --interval 120

  # Watch local directory and sync on changes
  %(prog)s watch protondrive:BSW-Arch/docs /opt/documentation

  # Setup Proton Drive integration
  %(prog)s setup
"""
    )

    parser.add_argument(
        "command",
        choices=["pull", "push", "both", "continuous", "watch", "setup"],
        help="Sync command to execute"
    )
    parser.add_argument(
        "remote_path",
        nargs="?",
        help="Proton Drive remote path (e.g., protondrive:BSW-Arch/docs)"
    )
    parser.add_argument(
        "local_path",
        nargs="?",
        default="/opt/documentation",
        help="Local directory path (default: /opt/documentation)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Polling interval in seconds for continuous mode (default: 60)"
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Disable automatic knowledge graph indexing"
    )

    args = parser.parse_args()

    if args.command == "setup":
        setup_proton_drive()
        return

    if not args.remote_path:
        print("Error: remote_path is required for sync commands")
        parser.print_help()
        sys.exit(1)

    sync = ProtonDriveSync(
        remote_path=args.remote_path,
        local_path=Path(args.local_path),
        poll_interval=args.interval,
        auto_index=not args.no_index
    )

    if args.command == "pull":
        sync.sync_once("pull")
    elif args.command == "push":
        sync.sync_once("push")
    elif args.command == "both":
        sync.sync_once("both")
    elif args.command == "continuous":
        sync.continuous_sync()
    elif args.command == "watch":
        watch_and_sync(sync)


if __name__ == "__main__":
    main()
