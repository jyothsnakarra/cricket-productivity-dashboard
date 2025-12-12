#!/usr/bin/env python3
"""
Enhanced Match Processor for Cricket Dashboard
Provides intelligent JSON file discovery, match metadata extraction, and caching
"""

import json
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime, timedelta
import hashlib
import pickle
from typing import Dict, List, Optional, Tuple, Any, Iterator, Generator
from dataclasses import dataclass
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc

# Optional psutil import for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchInfo:
    """Data class for match information"""
    match_id: str
    teams: List[str]
    venue: str
    date: str
    match_type: str
    event_name: str
    significance: str  # "Final", "World Cup", "Regular"
    outcome: Dict[str, Any]
    file_path: str

@dataclass
class MatchStats:
    """Data class for match statistics"""
    total_balls: int
    total_wickets: int
    total_runs: int
    match_duration_minutes: float
    innings_count: int
    highest_partnership: int
    best_bowling_figures: str
    match_winner: str

class EnhancedMatchProcessor:
    """Enhanced match processor with intelligent discovery, caching, and performance optimization"""
    
    def __init__(self, data_folder: str = "src/data", cache_folder: str = "src/cache", 
                 max_workers: int = 4, chunk_size: int = 1000, memory_limit_mb: int = 512):
        self.data_folder = data_folder
        self.cache_folder = cache_folder
        self.discovered_matches: Dict[str, MatchInfo] = {}
        self.processed_cache: Dict[str, pd.DataFrame] = {}
        
        # Performance optimization settings
        self.max_workers = min(max_workers, os.cpu_count() or 4)
        self.chunk_size = chunk_size
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        
        # Lazy loading state
        self._matches_discovered = False
        self._discovery_lock = threading.Lock()
        
        # Progress tracking
        self.progress_callback = None
        self.current_operation = None
        
        # Create cache folder if it doesn't exist
        os.makedirs(cache_folder, exist_ok=True)
        
        # Load cached matches on initialization (lazy)
        self._cache_loaded = False
    
    def discover_all_matches(self, lazy: bool = True, max_matches: int = None) -> Dict[str, MatchInfo]:
        """
        Scan src/data folder and extract match metadata from all JSON files with lazy loading
        Returns dictionary of match_name -> MatchInfo
        """
        with self._discovery_lock:
            if self._matches_discovered and lazy:
                return self.discovered_matches
            
            logger.info(f"Discovering matches in {self.data_folder}")
            self._update_progress("Scanning for match files...", 0)
            
            # Find all JSON files
            json_files = glob.glob(os.path.join(self.data_folder, "*.json"))
            total_files = len(json_files)
            logger.info(f"Found {total_files} JSON files")
            
            # Apply limit for performance
            if max_matches:
                json_files = json_files[:max_matches]
            elif total_files > 50:  # Default limit for performance
                json_files = json_files[:50]
                logger.info(f"Limited to first {len(json_files)} files for performance")
            
            matches = {}
            
            # Use parallel processing for better performance
            self._update_progress("Processing match metadata...", 10)
            
            if len(json_files) > 10 and self.max_workers > 1:
                matches = self._discover_matches_parallel(json_files)
            else:
                matches = self._discover_matches_sequential(json_files)
            
            self.discovered_matches = matches
            self._matches_discovered = True
            self._update_progress("Match discovery complete", 100)
            
            logger.info(f"Successfully discovered {len(matches)} matches")
            return matches
    
    def _discover_matches_parallel(self, json_files: List[str]) -> Dict[str, MatchInfo]:
        """Discover matches using parallel processing"""
        matches = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks
            future_to_file = {
                executor.submit(self._extract_match_metadata, json_file): json_file 
                for json_file in json_files
            }
            
            completed = 0
            total = len(json_files)
            
            for future in as_completed(future_to_file):
                json_file = future_to_file[future]
                completed += 1
                
                try:
                    match_info = future.result()
                    if match_info:
                        display_name = self._generate_match_display_name(match_info)
                        matches[display_name] = match_info
                        
                    # Update progress
                    progress = 10 + (completed / total) * 80
                    self._update_progress(f"Processed {completed}/{total} matches", progress)
                    
                except Exception as e:
                    logger.warning(f"Skipping {json_file}: {e}")
                    continue
        
        return matches
    
    def _discover_matches_sequential(self, json_files: List[str]) -> Dict[str, MatchInfo]:
        """Discover matches using sequential processing"""
        matches = {}
        total = len(json_files)
        
        for i, json_file in enumerate(json_files):
            try:
                match_info = self._extract_match_metadata(json_file)
                if match_info:
                    display_name = self._generate_match_display_name(match_info)
                    matches[display_name] = match_info
                
                # Update progress
                progress = 10 + ((i + 1) / total) * 80
                self._update_progress(f"Processed {i + 1}/{total} matches", progress)
                
            except Exception as e:
                logger.warning(f"Skipping {json_file}: {e}")
                continue
        
        return matches
    
    def _extract_match_metadata(self, file_path: str) -> Optional[MatchInfo]:
        """Extract metadata from a single JSON match file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                match_data = json.load(f)
            
            info = match_data.get('info', {})
            
            # Extract basic information
            teams = info.get('teams', ['Team A', 'Team B'])
            venue = info.get('venue', 'Unknown Venue')
            dates = info.get('dates', ['2024-01-01'])
            match_type = info.get('match_type', 'T20')
            event = info.get('event', {})
            event_name = event.get('name', 'Cricket Match') if isinstance(event, dict) else str(event)
            outcome = info.get('outcome', {})
            
            # Generate match ID from filename
            match_id = os.path.basename(file_path).replace('.json', '')
            
            # Determine match significance
            significance = self._determine_match_significance(event_name, info)
            
            return MatchInfo(
                match_id=match_id,
                teams=teams,
                venue=venue,
                date=dates[0] if dates else '2024-01-01',
                match_type=match_type,
                event_name=event_name,
                significance=significance,
                outcome=outcome,
                file_path=file_path
            )
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return None
    
    def _determine_match_significance(self, event_name: str, info: Dict) -> str:
        """Determine the significance of a match based on event name and other info"""
        event_lower = event_name.lower()
        
        # Check for finals
        if any(keyword in event_lower for keyword in ['final', 'championship']):
            return "Final"
        
        # Check for World Cup matches
        if any(keyword in event_lower for keyword in ['world cup', 'world t20', 'cwc']):
            return "World Cup"
        
        # Check for other major tournaments
        if any(keyword in event_lower for keyword in ['ipl', 'champions trophy', 'asia cup']):
            return "Major Tournament"
        
        # Check for international series
        if any(keyword in event_lower for keyword in ['test series', 'odi series', 't20i series']):
            return "International Series"
        
        return "Regular"
    
    def _generate_match_display_name(self, match_info: MatchInfo) -> str:
        """Generate user-friendly match display name with significance indicators"""
        # Start with teams
        if len(match_info.teams) >= 2:
            display_name = f"{match_info.teams[0]} vs {match_info.teams[1]}"
        else:
            display_name = f"Match {match_info.match_id}"
        
        # Add match type and date
        display_name += f" ({match_info.match_type}) - {match_info.date}"
        
        # Add significance indicators
        if match_info.significance == "Final":
            display_name += " 🏆"
        elif match_info.significance == "World Cup":
            display_name += " 🌍"
        elif match_info.significance == "Major Tournament":
            display_name += " ⭐"
        elif match_info.match_type == "T20":
            display_name += " ⚡"
        
        # Add venue if it's a famous ground
        famous_venues = ['Lord\'s', 'MCG', 'Eden Gardens', 'Wankhede', 'The Oval']
        if any(venue in match_info.venue for venue in famous_venues):
            display_name += f" @ {match_info.venue}"
        
        return display_name
    
    def _standardize_team_name(self, team_name: str) -> str:
        """Standardize team names for consistency"""
        # Common team name mappings
        team_mappings = {
            'Australia': 'Australia',
            'India': 'India', 
            'England': 'England',
            'Pakistan': 'Pakistan',
            'Sri Lanka': 'Sri Lanka',
            'South Africa': 'South Africa',
            'New Zealand': 'New Zealand',
            'West Indies': 'West Indies',
            'Bangladesh': 'Bangladesh',
            'Afghanistan': 'Afghanistan'
        }
        
        # Try to find exact match first
        if team_name in team_mappings:
            return team_mappings[team_name]
        
        # Try partial matching
        for standard_name in team_mappings.values():
            if standard_name.lower() in team_name.lower() or team_name.lower() in standard_name.lower():
                return standard_name
        
        # Return original if no match found
        return team_name
    
    def get_match_seed(self, match_id: str) -> int:
        """Generate consistent seed for match to ensure reproducible data"""
        return int(hashlib.md5(match_id.encode()).hexdigest()[:8], 16)
    
    def _get_cache_path(self, match_id: str) -> str:
        """Get cache file path for a match"""
        return os.path.join(self.cache_folder, f"{match_id}_processed.pkl")
    
    def _load_cache(self):
        """Load cached processed matches with memory management"""
        if self._cache_loaded:
            return
            
        try:
            self._update_progress("Loading cached matches...", 0)
            cache_files = glob.glob(os.path.join(self.cache_folder, "*_processed.pkl"))
            total_files = len(cache_files)
            
            loaded_count = 0
            memory_used = 0
            
            for i, cache_file in enumerate(cache_files):
                # Check memory usage
                if memory_used > self.memory_limit_bytes:
                    logger.warning(f"Memory limit reached, skipping remaining cache files")
                    break
                
                match_id = os.path.basename(cache_file).replace('_processed.pkl', '')
                try:
                    file_size = os.path.getsize(cache_file)
                    
                    # Skip large files if memory is constrained
                    if memory_used + file_size > self.memory_limit_bytes:
                        logger.info(f"Skipping large cache file {match_id} to preserve memory")
                        continue
                    
                    with open(cache_file, 'rb') as f:
                        self.processed_cache[match_id] = pickle.load(f)
                    
                    memory_used += file_size
                    loaded_count += 1
                    
                    # Update progress
                    progress = (i + 1) / total_files * 100
                    self._update_progress(f"Loaded {loaded_count}/{total_files} cached matches", progress)
                    
                except Exception as e:
                    logger.warning(f"Failed to load cache for {match_id}: {e}")
            
            self._cache_loaded = True
            logger.info(f"Loaded {loaded_count} cached matches ({memory_used / 1024 / 1024:.1f} MB)")
            
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            self._cache_loaded = True
    
    def _save_to_cache(self, match_id: str, data: pd.DataFrame):
        """Save processed match data to cache"""
        try:
            cache_path = self._get_cache_path(match_id)
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Cached processed data for match {match_id}")
        except Exception as e:
            logger.warning(f"Failed to cache match {match_id}: {e}")
    
    def is_cache_valid(self, match_id: str, file_path: str) -> bool:
        """Check if cached data is still valid (file hasn't been modified)"""
        cache_path = self._get_cache_path(match_id)
        
        if not os.path.exists(cache_path):
            return False
        
        try:
            cache_mtime = os.path.getmtime(cache_path)
            file_mtime = os.path.getmtime(file_path)
            return cache_mtime > file_mtime
        except Exception:
            return False
    
    def get_cached_match(self, match_id: str) -> Optional[pd.DataFrame]:
        """Retrieve cached match data if available"""
        return self.processed_cache.get(match_id)
    
    def invalidate_cache(self, match_id: str = None):
        """Invalidate cache for a specific match or all matches"""
        if match_id:
            # Remove specific match from cache
            if match_id in self.processed_cache:
                del self.processed_cache[match_id]
            
            cache_path = self._get_cache_path(match_id)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.info(f"Invalidated cache for match {match_id}")
        else:
            # Clear all cache
            self.processed_cache.clear()
            cache_files = glob.glob(os.path.join(self.cache_folder, "*_processed.pkl"))
            for cache_file in cache_files:
                os.remove(cache_file)
            logger.info("Invalidated all cached matches")
    
    def process_match_data(self, match_file: str, use_chunking: bool = True) -> pd.DataFrame:
        """
        Convert JSON match file to dashboard format with performance optimizations
        Handles various JSON structures gracefully with memory management
        """
        try:
            self._update_progress("Loading match file...", 0)
            
            # Check file size first
            file_size = os.path.getsize(match_file)
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                logger.warning(f"Large file detected ({file_size / 1024 / 1024:.1f} MB), using streaming")
                return self._process_large_match_file(match_file)
            
            with open(match_file, 'r', encoding='utf-8') as f:
                match_data = json.load(f)
            
            self._update_progress("Extracting match metadata...", 20)
            
            # Extract match info
            match_info = self._extract_match_metadata(match_file)
            if not match_info:
                return pd.DataFrame()
            
            # Check cache first (lazy load cache if needed)
            if not self._cache_loaded:
                self._load_cache()
            
            if self.is_cache_valid(match_info.match_id, match_file):
                cached_data = self.get_cached_match(match_info.match_id)
                if cached_data is not None:
                    logger.info(f"Using cached data for {match_info.match_id}")
                    self._update_progress("Loaded from cache", 100)
                    return cached_data
            
            self._update_progress("Processing match data...", 40)
            
            # Process innings data with chunking if enabled
            if use_chunking and len(match_data.get('innings', [])) > 2:
                df = self._process_innings_data_chunked(match_data, match_info)
            else:
                df = self._process_innings_data(match_data, match_info)
            
            self._update_progress("Caching processed data...", 90)
            
            # Cache the processed data (with memory check)
            if self._check_memory_usage():
                self._save_to_cache(match_info.match_id, df)
                self.processed_cache[match_info.match_id] = df
            else:
                logger.warning("Memory limit reached, skipping cache save")
            
            self._update_progress("Processing complete", 100)
            return df
            
        except Exception as e:
            logger.error(f"Error processing match file {match_file}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    def _process_innings_data(self, match_data: dict, match_info: MatchInfo) -> pd.DataFrame:
        """Process innings data from JSON into timeline format"""
        
        # Set seed for consistent data generation
        np.random.seed(self.get_match_seed(match_info.match_id))
        
        innings = match_data.get('innings', [])
        
        # Create realistic match start time
        match_start = self._calculate_match_start_time(match_info)
        
        timeline_data = []
        current_time = match_start
        
        for inning_idx, inning in enumerate(innings):
            team = inning.get('team', f'Team {inning_idx + 1}')
            overs = inning.get('overs', [])
            wickets_in_innings = 0  # Track wickets per innings
            
            for over in overs:
                over_number = over.get('over', 0)
                deliveries = over.get('deliveries', [])
                
                for ball_idx, delivery in enumerate(deliveries):
                    # Check if this delivery has a wicket
                    wickets = delivery.get('wickets', [])
                    has_wicket = len(wickets) > 0
                    
                    # Validate wicket count (max 10 per innings in cricket)
                    if has_wicket and wickets_in_innings >= 10:
                        # Skip this wicket to maintain cricket rules
                        has_wicket = False
                        delivery = delivery.copy()
                        delivery['wickets'] = []
                    elif has_wicket:
                        wickets_in_innings += 1
                    
                    # Extract ball data
                    ball_data = self._extract_ball_data(
                        delivery, over_number, ball_idx, inning_idx + 1, 
                        current_time, match_info
                    )
                    
                    timeline_data.append(ball_data)
                    
                    # Advance time (realistic ball intervals)
                    current_time += timedelta(seconds=np.random.randint(20, 50))
        
        # Convert to DataFrame
        df = pd.DataFrame(timeline_data)
        
        # Add calculated fields
        if not df.empty:
            df = self._add_calculated_fields(df, match_info)
        
        return df
    
    def _calculate_match_start_time(self, match_info: MatchInfo) -> datetime:
        """Calculate realistic match start time based on teams and match type"""
        
        base_date = datetime.strptime(match_info.date, "%Y-%m-%d")
        
        # Different start times based on teams and match type
        teams = match_info.teams
        
        if any('India' in team or 'Pakistan' in team or 'Sri Lanka' in team for team in teams):
            # Subcontinent matches - evening start
            start_hour = 19
        elif any('Australia' in team or 'New Zealand' in team for team in teams):
            # Australia/NZ matches - afternoon start  
            start_hour = 14
        elif any('England' in team or 'South Africa' in team for team in teams):
            # England/SA matches - varied timing
            start_hour = 16
        else:
            # Default timing
            start_hour = 18
        
        # Add some randomness
        start_hour += np.random.randint(-1, 2)
        start_minute = np.random.choice([0, 15, 30, 45])
        
        return base_date.replace(hour=start_hour, minute=start_minute, second=0)
    
    def _extract_ball_data(self, delivery: dict, over_number: int, ball_idx: int, 
                          innings: int, timestamp: datetime, match_info: MatchInfo) -> dict:
        """Extract data for a single ball/delivery"""
        
        # Extract runs
        runs_data = delivery.get('runs', {})
        total_runs = runs_data.get('total', 0)
        batter_runs = runs_data.get('batter', 0)
        extras = runs_data.get('extras', 0)
        
        # Extract wicket information
        wickets = delivery.get('wickets', [])
        is_wicket = len(wickets) > 0
        
        # Generate commentary
        commentary = self._generate_commentary(delivery, is_wicket, total_runs, wickets)
        
        # Extract player information
        batter = delivery.get('batter', f'Batter{np.random.randint(1, 12)}')
        bowler = delivery.get('bowler', f'Bowler{np.random.randint(1, 12)}')
        
        return {
            'timestamp_utc': timestamp.isoformat(),
            'over': over_number + 1,  # Convert to 1-based
            'ball': ball_idx + 1,     # Convert to 1-based
            'runs': total_runs,
            'batter_runs': batter_runs,
            'extras': extras,
            'is_wicket': is_wicket,
            'wicket_info': wickets[0] if wickets else None,
            'commentary_text': commentary,
            'batter': batter,
            'bowler': bowler,
            'innings': innings,
            'match_id': match_info.match_id,
            'teams': f"{match_info.teams[0]} vs {match_info.teams[1]}",
            'venue': match_info.venue,
            'match_type': match_info.match_type,
            'event': match_info.event_name
        }
    
    def _generate_commentary(self, delivery: dict, is_wicket: bool, 
                           runs: int, wickets: List[dict]) -> str:
        """Generate realistic commentary for a delivery"""
        
        batter = delivery.get('batter', 'Batsman')
        bowler = delivery.get('bowler', 'Bowler')
        
        if is_wicket and wickets:
            wicket = wickets[0]
            wicket_type = wicket.get('kind', 'out')
            player_out = wicket.get('player_out', batter)
            
            if wicket_type == 'caught':
                fielders = wicket.get('fielders', [])
                if fielders:
                    fielder = fielders[0].get('name', 'fielder')
                    return f"WICKET! {player_out} caught by {fielder} off {bowler}"
                else:
                    return f"WICKET! {player_out} caught off {bowler}"
            elif wicket_type == 'bowled':
                return f"BOWLED! {bowler} crashes through {player_out}'s defenses"
            elif wicket_type == 'lbw':
                return f"LBW! {player_out} trapped in front by {bowler}"
            elif wicket_type == 'run out':
                return f"RUN OUT! {player_out} caught short of the crease"
            elif wicket_type == 'stumped':
                return f"STUMPED! {player_out} beaten by the keeper"
            else:
                return f"WICKET! {player_out} {wicket_type} off {bowler}"
        
        elif runs == 6:
            return f"SIX! {batter} launches {bowler} into the stands!"
        elif runs == 4:
            return f"FOUR! Brilliant shot by {batter} off {bowler}"
        elif runs == 0:
            return f"Dot ball. {bowler} beats {batter}"
        else:
            return f"{batter} works {bowler} for {runs} run(s)"
    
    def _add_calculated_fields(self, df: pd.DataFrame, match_info: MatchInfo) -> pd.DataFrame:
        """Add calculated fields to the DataFrame"""
        
        # Convert timestamp to datetime
        df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
        
        # Calculate match minute
        match_start = df['timestamp_utc'].iloc[0]
        df['match_minute'] = (df['timestamp_utc'] - match_start).dt.total_seconds() / 60
        
        # Calculate cumulative runs by innings
        df['cumulative_runs'] = df.groupby('innings')['runs'].cumsum()
        
        # Calculate run rate
        df['balls_faced'] = df.groupby('innings').cumcount() + 1
        df['run_rate'] = (df['cumulative_runs'] / df['balls_faced'] * 6).round(2)
        
        # Calculate runs per over for current over
        df['runs_per_over'] = df.groupby(['innings', 'over'])['runs'].transform('sum')
        
        # Add GitHub commit simulation (for dashboard compatibility)
        df = self._add_github_simulation(df, match_info)
        
        return df
    
    def _add_github_simulation(self, df: pd.DataFrame, match_info: MatchInfo) -> pd.DataFrame:
        """Add simulated GitHub commit data for dashboard compatibility"""
        
        # Set seed for consistent simulation
        np.random.seed(self.get_match_seed(match_info.match_id))
        
        # Base commit rate varies by match characteristics
        teams = match_info.teams
        if any('India' in team for team in teams):
            base_rate = 180
        elif 'World Cup' in match_info.event_name:
            base_rate = 200
        elif match_info.significance == 'Final':
            base_rate = 220
        else:
            base_rate = 140
        
        # Generate commit counts
        commit_counts = []
        commit_velocities = []
        commit_drops = []
        
        for idx, row in df.iterrows():
            # Time-based variation
            hour = row['timestamp_utc'].hour
            if 9 <= hour <= 17:
                time_multiplier = 1.3
            elif 18 <= hour <= 22:
                time_multiplier = 1.0
            else:
                time_multiplier = 0.4
            
            # Base commits
            base_commits = int(np.random.poisson(base_rate * time_multiplier / 12))  # Per ball
            
            # Wicket impact
            impact_factor = 1.0
            if row['is_wicket']:
                impact_factor = np.random.uniform(0.4, 0.7)  # 30-60% drop
            elif row['runs'] >= 4:
                impact_factor = np.random.uniform(0.8, 0.95)  # Small drop for big hits
            
            final_commits = max(5, int(base_commits * impact_factor))
            commit_counts.append(final_commits)
            
            # Calculate velocity (smoothed)
            if len(commit_counts) >= 3:
                velocity = np.mean(commit_counts[-3:])
            else:
                velocity = final_commits
            commit_velocities.append(velocity)
            
            # Calculate drop percentage for wickets
            if row['is_wicket']:
                drop_pct = (1 - impact_factor) * 100
            else:
                drop_pct = 0.0
            commit_drops.append(drop_pct)
        
        df['commit_count'] = commit_counts
        df['commit_velocity'] = commit_velocities
        df['commit_drop_percentage'] = commit_drops
        
        return df
    
    def get_cache_size(self) -> Dict[str, Any]:
        """Get cache size information"""
        try:
            cache_files = glob.glob(os.path.join(self.cache_folder, "*_processed.pkl"))
            
            total_size = 0
            file_count = len(cache_files)
            
            for cache_file in cache_files:
                try:
                    total_size += os.path.getsize(cache_file)
                except Exception:
                    continue
            
            # Convert to human readable format
            if total_size < 1024:
                size_str = f"{total_size} B"
            elif total_size < 1024 * 1024:
                size_str = f"{total_size / 1024:.1f} KB"
            else:
                size_str = f"{total_size / (1024 * 1024):.1f} MB"
            
            return {
                'total_size_bytes': total_size,
                'total_size_human': size_str,
                'file_count': file_count,
                'in_memory_count': len(self.processed_cache)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache size: {e}")
            return {'error': str(e)}
    
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, message: str, progress: float):
        """Update progress with callback if available"""
        self.current_operation = message
        if self.progress_callback:
            self.progress_callback(message, progress)
        else:
            logger.info(f"Progress: {progress:.1f}% - {message}")
    
    def _check_memory_usage(self) -> bool:
        """Check if current memory usage is within limits"""
        if not PSUTIL_AVAILABLE:
            return True  # Default to allowing operation if psutil not available
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss < self.memory_limit_bytes
        except Exception:
            return True  # Default to allowing operation if check fails
    
    def _process_large_match_file(self, match_file: str) -> pd.DataFrame:
        """Process large match files using streaming approach"""
        logger.info(f"Processing large file {match_file} with streaming")
        
        try:
            # For very large files, we'll process in chunks
            # This is a simplified approach - in production, you'd use ijson or similar
            with open(match_file, 'r', encoding='utf-8') as f:
                match_data = json.load(f)
            
            match_info = self._extract_match_metadata(match_file)
            if not match_info:
                return pd.DataFrame()
            
            # Process with chunking
            return self._process_innings_data_chunked(match_data, match_info)
            
        except Exception as e:
            logger.error(f"Error processing large file {match_file}: {e}")
            return pd.DataFrame()
    
    def _process_innings_data_chunked(self, match_data: dict, match_info: MatchInfo) -> pd.DataFrame:
        """Process innings data in chunks for better memory management"""
        logger.info("Processing match data in chunks for better performance")
        
        # Set seed for consistent data generation
        np.random.seed(self.get_match_seed(match_info.match_id))
        
        innings = match_data.get('innings', [])
        match_start = self._calculate_match_start_time(match_info)
        
        all_chunks = []
        current_time = match_start
        
        for inning_idx, inning in enumerate(innings):
            team = inning.get('team', f'Team {inning_idx + 1}')
            overs = inning.get('overs', [])
            wickets_in_innings = 0
            
            # Process overs in chunks
            over_chunks = [overs[i:i + self.chunk_size] for i in range(0, len(overs), self.chunk_size)]
            
            for chunk_idx, over_chunk in enumerate(over_chunks):
                chunk_data = []
                
                for over in over_chunk:
                    over_number = over.get('over', 0)
                    deliveries = over.get('deliveries', [])
                    
                    for ball_idx, delivery in enumerate(deliveries):
                        # Check wicket limits
                        wickets = delivery.get('wickets', [])
                        has_wicket = len(wickets) > 0
                        
                        if has_wicket and wickets_in_innings >= 10:
                            has_wicket = False
                            delivery = delivery.copy()
                            delivery['wickets'] = []
                        elif has_wicket:
                            wickets_in_innings += 1
                        
                        # Extract ball data
                        ball_data = self._extract_ball_data(
                            delivery, over_number, ball_idx, inning_idx + 1, 
                            current_time, match_info
                        )
                        
                        chunk_data.append(ball_data)
                        current_time += timedelta(seconds=np.random.randint(20, 50))
                
                # Convert chunk to DataFrame and add to collection
                if chunk_data:
                    chunk_df = pd.DataFrame(chunk_data)
                    all_chunks.append(chunk_df)
                
                # Update progress
                total_chunks = sum(len(overs) // self.chunk_size + 1 for inning in innings for overs in [inning.get('overs', [])])
                current_chunk = chunk_idx + 1 + inning_idx * len(over_chunks)
                progress = 40 + (current_chunk / total_chunks) * 40
                self._update_progress(f"Processing chunk {current_chunk}/{total_chunks}", progress)
                
                # Garbage collection for memory management
                if chunk_idx % 5 == 0:
                    gc.collect()
        
        # Combine all chunks
        if all_chunks:
            df = pd.concat(all_chunks, ignore_index=True)
            
            # Add calculated fields
            df = self._add_calculated_fields(df, match_info)
            
            return df
        else:
            return pd.DataFrame()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        if not PSUTIL_AVAILABLE:
            return {
                'rss_mb': 0,
                'vms_mb': 0,
                'percent': 0,
                'limit_mb': self.memory_limit_bytes / 1024 / 1024,
                'cached_matches': len(self.processed_cache),
                'cache_size_mb': sum(df.memory_usage(deep=True).sum() for df in self.processed_cache.values()) / 1024 / 1024 if self.processed_cache else 0,
                'psutil_available': False
            }
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent(),
                'limit_mb': self.memory_limit_bytes / 1024 / 1024,
                'cached_matches': len(self.processed_cache),
                'cache_size_mb': sum(df.memory_usage(deep=True).sum() for df in self.processed_cache.values()) / 1024 / 1024 if self.processed_cache else 0,
                'psutil_available': True
            }
        except Exception as e:
            return {'error': str(e), 'psutil_available': True}
    
    def cleanup_memory(self, force: bool = False):
        """Clean up memory by removing cached data"""
        if force or not self._check_memory_usage():
            logger.info("Cleaning up memory cache")
            
            # Remove oldest cached matches first
            if self.processed_cache:
                # Simple cleanup - remove half of cached data
                items_to_remove = len(self.processed_cache) // 2
                keys_to_remove = list(self.processed_cache.keys())[:items_to_remove]
                
                for key in keys_to_remove:
                    del self.processed_cache[key]
                
                logger.info(f"Removed {items_to_remove} cached matches from memory")
            
            # Force garbage collection
            gc.collect()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'max_workers': self.max_workers,
            'chunk_size': self.chunk_size,
            'memory_limit_mb': self.memory_limit_bytes / 1024 / 1024,
            'matches_discovered': len(self.discovered_matches),
            'cache_loaded': self._cache_loaded,
            'current_operation': self.current_operation,
            **self.get_memory_stats()
        }


# Global instance for backward compatibility
enhanced_processor = EnhancedMatchProcessor()

def get_enhanced_processor() -> EnhancedMatchProcessor:
    """Get the global enhanced processor instance"""
    return enhanced_processor

# Enhanced backward compatibility functions
def get_available_matches():
    """Get all available matches using enhanced processor"""
    processor = get_enhanced_processor()
    matches = processor.discover_all_matches()
    
    # Convert to format expected by existing dashboard
    dashboard_matches = {}
    for match_name, match_info in matches.items():
        dashboard_matches[match_name] = {
            'file': match_info.file_path,
            'match_id': match_info.match_id,
            'teams': match_info.teams,
            'date': match_info.date,
            'event': match_info.event_name,
            'match_type': match_info.match_type,
            'venue': match_info.venue,
            'significance': match_info.significance,
            'outcome': match_info.outcome,
            'info': {
                'teams': match_info.teams,
                'venue': match_info.venue,
                'dates': [match_info.date],
                'match_type': match_info.match_type,
                'event': {'name': match_info.event_name},
                'outcome': match_info.outcome
            }
        }
    
    return dashboard_matches

def load_match_data(match_name: str, match_info: dict):
    """Load match data using enhanced processor"""
    processor = get_enhanced_processor()
    
    # Get file path from match_info
    file_path = match_info.get('file', '')
    if not file_path:
        logger.error(f"No file path provided for match {match_name}")
        return pd.DataFrame()
    
    # Process the match
    return processor.process_match_data(file_path)

if __name__ == "__main__":
    # Test the enhanced processor
    processor = EnhancedMatchProcessor()
    
    print("Testing Enhanced Match Processor...")
    
    # Test match discovery
    matches = processor.discover_all_matches()
    print(f"Discovered {len(matches)} matches")
    
    if matches:
        # Test processing first match
        first_match_name = list(matches.keys())[0]
        first_match_info = matches[first_match_name]
        
        print(f"\nTesting with: {first_match_name}")
        print(f"Teams: {first_match_info.teams}")
        print(f"Venue: {first_match_info.venue}")
        print(f"Date: {first_match_info.date}")
        print(f"Significance: {first_match_info.significance}")
        
        # Process match data
        df = processor.process_match_data(first_match_info.file_path)
        
        if not df.empty:
            print(f"\nProcessed data:")
            print(f"Total balls: {len(df)}")
            print(f"Total wickets: {df['is_wicket'].sum()}")
            print(f"Wickets by innings: {df.groupby('innings')['is_wicket'].sum().to_dict()}")
            print(f"Total runs: {df['runs'].sum()}")
            print(f"Match duration: {df['match_minute'].max():.1f} minutes")
        
        # Test cache info
        cache_size = processor.get_cache_size()
        print(f"\nCache size: {cache_size}")
    
    else:
        print("No matches found in data folder")