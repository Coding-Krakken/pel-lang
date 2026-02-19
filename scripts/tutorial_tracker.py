#!/usr/bin/env python3
"""
Tutorial Progress Tracker - Interactive learning progress tracker

Helps users track their progress through the PEL tutorial suite.
Stores completion status and provides recommendations for next steps.

Usage:
    # View progress
    python scripts/tutorial_tracker.py
    
    # Mark tutorial as completed
    python scripts/tutorial_tracker.py --complete 01
    
    # Reset progress
    python scripts/tutorial_tracker.py --reset
    
    # Get recommendation for next tutorial
    python scripts/tutorial_tracker.py --next
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set


class TutorialTracker:
    """Track tutorial completion progress."""
    
    TUTORIALS = {
        "01": {
            "name": "Your First Model in 15 Minutes",
            "time": 15,
            "difficulty": "Beginner",
            "prerequisites": [],
        },
        "02": {
            "name": "Understanding Economic Types",
            "time": 20,
            "difficulty": "Beginner",
            "prerequisites": ["01"],
        },
        "03": {
            "name": "Uncertainty & Distributions",
            "time": 25,
            "difficulty": "Beginner",
            "prerequisites": ["01"],
        },
        "04": {
            "name": "Constraints & Policies",
            "time": 25,
            "difficulty": "Intermediate",
            "prerequisites": ["01", "02", "03"],
        },
        "05": {
            "name": "Provenance & Assumption Governance",
            "time": 20,
            "difficulty": "Intermediate",
            "prerequisites": ["01", "02"],
        },
        "06": {
            "name": "Time-Series Modeling",
            "time": 30,
            "difficulty": "Intermediate",
            "prerequisites": ["01", "02"],
        },
        "07": {
            "name": "Stdlib Functions & Modules",
            "time": 25,
            "difficulty": "Intermediate",
            "prerequisites": ["01", "02", "03", "04", "05", "06"],
        },
        "08": {
            "name": "Calibration Basics",
            "time": 30,
            "difficulty": "Advanced",
            "prerequisites": ["01", "02", "03", "04", "05", "06", "07"],
        },
        "09": {
            "name": "Migration from Spreadsheets",
            "time": 40,
            "difficulty": "Advanced",
            "prerequisites": ["01", "02", "05", "06"],
        },
        "10": {
            "name": "Production Deployment",
            "time": 35,
            "difficulty": "Advanced",
            "prerequisites": ["01", "02", "03", "04", "05", "06", "07", "08"],
        },
    }
    
    LEARNING_PATHS = {
        "quick_start": {
            "name": "Quick Start",
            "tutorials": ["01", "02", "03"],
            "time": 60,
            "outcome": "Can build and run basic PEL models",
        },
        "spreadsheet_migration": {
            "name": "Spreadsheet Migration",
            "tutorials": ["01", "02", "05", "06", "09", "04"],
            "time": 180,
            "outcome": "Can migrate Excel models to PEL",
        },
        "production_ready": {
            "name": "Production-Ready",
            "tutorials": ["01", "02", "03", "04", "05", "06", "07", "08", "10"],
            "time": 300,
            "outcome": "Can build, test, and deploy production models",
        },
        "full_mastery": {
            "name": "Full Mastery",
            "tutorials": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"],
            "time": 270,
            "outcome": "Complete PEL expertise",
        },
    }
    
    def __init__(self, progress_file: Path = None):
        if progress_file is None:
            progress_file = Path.home() / ".pel_tutorial_progress.json"
        
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load progress from file."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        return {
            "completed": [],
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }
    
    def _save_progress(self):
        """Save progress to file."""
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def mark_complete(self, tutorial_id: str):
        """Mark a tutorial as completed."""
        if tutorial_id not in self.TUTORIALS:
            print(f"❌ Unknown tutorial: {tutorial_id}")
            return False
        
        if tutorial_id not in self.progress["completed"]:
            self.progress["completed"].append(tutorial_id)
            self._save_progress()
            
            tutorial = self.TUTORIALS[tutorial_id]
            print(f"✅ Completed: {tutorial['name']}")
            print(f"   Time invested: {tutorial['time']} minutes")
            
            # Show total progress
            total = len(self.progress["completed"])
            print(f"\n📊 Progress: {total}/10 tutorials completed")
            
            # Suggest next tutorial
            next_tutorial = self.suggest_next()
            if next_tutorial:
                print(f"\n💡 Suggested next: Tutorial {next_tutorial}")
            else:
                print(f"\n🎉 Congratulations! You've completed all tutorials!")
            
            return True
        else:
            print(f"ℹ️  Already marked as completed: {tutorial_id}")
            return False
    
    def get_available_tutorials(self) -> List[str]:
        """Get list of tutorials that can be started (prerequisites met)."""
        completed = set(self.progress["completed"])
        available = []
        
        for tid, tutorial in self.TUTORIALS.items():
            if tid in completed:
                continue
            
            prereqs = set(tutorial["prerequisites"])
            if prereqs.issubset(completed):
                available.append(tid)
        
        return sorted(available)
    
    def suggest_next(self) -> str:
        """Suggest next tutorial based on prerequisites and learning path."""
        available = self.get_available_tutorials()
        
        if not available:
            return None
        
        # If Tutorial 01 is available, always suggest it
        if "01" in available:
            return "01"
        
        # Otherwise, suggest the first available in numerical order
        return available[0]
    
    def show_progress(self):
        """Display current progress."""
        completed = set(self.progress["completed"])
        total_time = sum(
            self.TUTORIALS[tid]["time"]
            for tid in completed
        )
        
        print("📚 PEL Tutorial Progress Tracker")
        print("=" * 70)
        print(f"\n✅ Completed: {len(completed)}/10 tutorials")
        print(f"⏱️  Time invested: {total_time} minutes ({total_time//60}h {total_time%60}m)")
        
        if self.progress.get("started_at"):
            started = datetime.fromisoformat(self.progress["started_at"])
            print(f"📅 Started: {started.strftime('%Y-%m-%d')}")
        
        print("\n" + "=" * 70)
        print("Tutorial Status:")
        print("=" * 70)
        
        for tid, tutorial in self.TUTORIALS.items():
            status = "✅" if tid in completed else "⬜"
            prereqs_met = set(tutorial["prerequisites"]).issubset(completed)
            
            available = ""
            if tid not in completed:
                if prereqs_met:
                    available = " [AVAILABLE]"
                else:
                    available = " [Locked]"
            
            print(f"{status} Tutorial {tid}: {tutorial['name']}{available}")
            print(f"   {tutorial['time']}min | {tutorial['difficulty']}")
        
        print("\n" + "=" * 70)
        
        # Show learning path progress
        print("\nLearning Path Progress:")
        print("=" * 70)
        
        for path_id, path in self.LEARNING_PATHS.items():
            path_completed = [t for t in path["tutorials"] if t in completed]
            progress = len(path_completed) / len(path["tutorials"]) * 100
            
            bar_length = 30
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"{path['name']:20} [{bar}] {progress:.0f}%")
        
        # Suggest next
        next_tutorial = self.suggest_next()
        if next_tutorial:
            print("\n" + "=" * 70)
            print(f"💡 Suggested next: Tutorial {next_tutorial}")
            print(f"   {self.TUTORIALS[next_tutorial]['name']}")
            print(f"   Time: {self.TUTORIALS[next_tutorial]['time']} minutes")
        else:
            print("\n" + "=" * 70)
            print("🎉 Congratulations! All tutorials completed!")
    
    def reset(self):
        """Reset all progress."""
        self.progress = {
            "completed": [],
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }
        self._save_progress()
        print("✅ Progress reset")


def main():
    parser = argparse.ArgumentParser(
        description="Track your progress through PEL tutorials"
    )
    parser.add_argument(
        "--complete",
        metavar="TUTORIAL_ID",
        help="Mark tutorial as completed (e.g., 01, 02, etc.)"
    )
    parser.add_argument(
        "--next",
        action="store_true",
        help="Show suggested next tutorial"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset all progress"
    )
    parser.add_argument(
        "--progress-file",
        type=Path,
        help="Custom progress file location"
    )
    
    args = parser.parse_args()
    
    tracker = TutorialTracker(progress_file=args.progress_file)
    
    if args.reset:
        tracker.reset()
    elif args.complete:
        tracker.mark_complete(args.complete)
    elif args.next:
        next_tutorial = tracker.suggest_next()
        if next_tutorial:
            tutorial = tracker.TUTORIALS[next_tutorial]
            print(f"Tutorial {next_tutorial}: {tutorial['name']}")
            print(f"Time: {tutorial['time']} minutes")
            print(f"Difficulty: {tutorial['difficulty']}")
        else:
            print("🎉 All tutorials completed!")
    else:
        tracker.show_progress()


if __name__ == "__main__":
    main()
