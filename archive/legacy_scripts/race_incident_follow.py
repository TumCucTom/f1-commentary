#!/usr/bin/env python3
"""
F1 Race Incident Follow Script

This script creates animated visualizations of specific incidents or moments during F1 races,
allowing you to follow two drivers at a specific part of a specific lap. Perfect for matching
up with commentary to show what actually happened.

Usage:
    python race_incident_follow.py --year 2024 --race "Hungary" --driver1 "VER" --driver2 "HAM" --lap 63 --start_time "13:45:30" --duration 30
    python race_incident_follow.py --year 2024 --race "Hungary" --driver1 "VER" --driver2 "HAM" --lap 63 --start_time "13:45:30" --duration 30 --follow --road
"""

import argparse
import sys
import os
import fastf1
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, List
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image


def load_track_data(track_name: str) -> Optional[pd.DataFrame]:
    """Load track centerline and edge data from CSV file."""
    try:
        csv_path = f"f1-ghost-car/track_data/{track_name}.csv"
        if os.path.exists(csv_path):
            # Read CSV, skipping the header comment line
            df = pd.read_csv(csv_path, comment='#', names=['x_m', 'y_m', 'w_tr_right_m', 'w_tr_left_m'])
            return df
        else:
            print(f"Track data file not found: {csv_path}")
            return None
    except Exception as e:
        print(f"Error loading track data: {e}")
        return None


def create_road_from_track_data(track_df: pd.DataFrame, data1_track: pd.DataFrame, data2_track: pd.DataFrame, ax=None):
    """Create road surface from track centerline and edge data, aligned with driver positions."""
    import numpy as np
    from scipy.spatial.distance import cdist
    from scipy.optimize import minimize
    
    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt
    
    # Get centerline coordinates
    center_x = track_df['x_m'].values
    center_y = track_df['y_m'].values
    
    # Get edge distances
    right_dist = track_df['w_tr_right_m'].values
    left_dist = track_df['w_tr_left_m'].values
    
    # Combine driver data to find the racing line
    driver_x = np.concatenate([data1_track['X'].values, data2_track['X'].values])
    driver_y = np.concatenate([data1_track['Y'].values, data2_track['Y'].values])
    
    # Find the best alignment between track data and driver data
    def alignment_error(params):
        scale, tx, ty = params
        
        # Scale and translate the track data
        scaled_center_x = center_x * scale + tx
        scaled_center_y = center_y * scale + ty
        
        # Find the best translation by minimizing distance to driver points
        track_points = np.column_stack([scaled_center_x, scaled_center_y])
        driver_points = np.column_stack([driver_x, driver_y])
        
        # Calculate minimum distances from each driver point to track
        distances = cdist(driver_points, track_points)
        min_distances = np.min(distances, axis=1)
        
        # Add penalty for points that are too far from track
        penalty = np.sum(np.maximum(0, min_distances - 30))  # Reduced penalty threshold
        
        return np.mean(min_distances) + penalty * 0.2
    
    # Try multiple starting points for better optimization
    best_result = None
    best_error = float('inf')
    
    # Test different starting points
    starting_points = [
        [9.717, -1000, -272],  # Previous result
        [8.875, 0, 0],         # Original scale
        [10.0, -500, -100],    # Larger scale, moderate shift
        [9.0, -1500, -400],    # Smaller scale, larger shift
        [11.0, -800, -200],    # Even larger scale
    ]
    
    for start_point in starting_points:
        try:
            result = minimize(alignment_error, start_point, 
                             bounds=[(5.0, 15.0), (-2000, 2000), (-2000, 2000)],
                             method='L-BFGS-B')
            
            if result.fun < best_error:
                best_error = result.fun
                best_result = result
        except:
            continue
    
    if best_result is None:
        # Fallback to simple optimization
        best_result = minimize(alignment_error, [9.717, -1000, -272], 
                              bounds=[(5.0, 15.0), (-2000, 2000), (-2000, 2000)],
                              method='L-BFGS-B')
    
    optimal_scale, optimal_tx, optimal_ty = best_result.x
    
    # Apply optimal transformation
    aligned_center_x = center_x * optimal_scale + optimal_tx
    aligned_center_y = center_y * optimal_scale + optimal_ty
    
    # Scale the edge distances as well
    scaled_right_dist = right_dist * optimal_scale
    scaled_left_dist = left_dist * optimal_scale
    
    # Calculate direction vectors along the track
    dx = np.gradient(aligned_center_x)
    dy = np.gradient(aligned_center_y)
    
    # Normalize direction vectors
    length = np.sqrt(dx**2 + dy**2)
    dx_norm = dx / length
    dy_norm = dy / length
    
    # Calculate perpendicular vectors (rotated 90 degrees)
    perp_x = -dy_norm
    perp_y = dx_norm
    
    # Create left and right edge points
    left_x = aligned_center_x + perp_x * scaled_left_dist
    left_y = aligned_center_y + perp_y * scaled_left_dist
    right_x = aligned_center_x - perp_x * scaled_right_dist
    right_y = aligned_center_y - perp_y * scaled_right_dist
    
    # Create road polygon by combining left and right edges
    road_x = np.concatenate([left_x, right_x[::-1]])
    road_y = np.concatenate([left_y, right_y[::-1]])
    
    # Plot the road as a filled polygon
    ax.fill(road_x, road_y, color='#808080', alpha=0.6, zorder=1, label='Road Surface')
    
    # Add road outline
    ax.plot(road_x, road_y, color='#606060', linewidth=2, alpha=0.8, zorder=2)
    
    # Calculate final alignment quality
    track_points = np.column_stack([aligned_center_x, aligned_center_y])
    driver_points = np.column_stack([driver_x, driver_y])
    distances = cdist(driver_points, track_points)
    min_distances = np.min(distances, axis=1)
    avg_distance = np.mean(min_distances)
    max_distance = np.max(min_distances)
    
    print(f"Track aligned with scale: {optimal_scale:.3f}, translation: ({optimal_tx:.1f}, {optimal_ty:.1f})")
    print(f"Alignment quality - Avg distance: {avg_distance:.1f}m, Max distance: {max_distance:.1f}m")
    
    return True


def load_car_image(driver_code: str, size: int = 30, rotation: float = 0, maintain_aspect: bool = False) -> Optional[Image.Image]:
    """Load car image for a driver with optional rotation and aspect ratio preservation."""
    try:
        image_path = f"f1-ghost-car/assets/cars/{driver_code.lower()}.png"
        if os.path.exists(image_path):
            img = Image.open(image_path)
            original_width, original_height = img.size
            
            if maintain_aspect:
                # Maintain aspect ratio - use size as the longer dimension
                aspect_ratio = original_width / original_height
                if aspect_ratio > 1:  # Wider than tall
                    new_width = size
                    new_height = int(size / aspect_ratio)
                else:  # Taller than wide or square
                    new_height = size
                    new_width = int(size * aspect_ratio)
                
                # Use even higher resolution for better quality when maintaining aspect ratio
                high_res_multiplier = 8  # 8x resolution for better quality
                high_res_width = new_width * high_res_multiplier
                high_res_height = new_height * high_res_multiplier
                
                img = img.resize((high_res_width, high_res_height), Image.Resampling.LANCZOS)
                
                # Rotate the image if needed (at high resolution)
                if rotation != 0:
                    img = img.rotate(rotation, expand=True, fillcolor=(255, 255, 255, 0))
                    # After rotation, we need to recalculate the final size to maintain aspect ratio
                    # Get the rotated dimensions
                    rotated_width, rotated_height = img.size
                    # Calculate the scale factor to fit within our target size
                    scale_factor = min(new_width / rotated_width, new_height / rotated_height)
                    final_width = int(rotated_width * scale_factor)
                    final_height = int(rotated_height * scale_factor)
                    # Resize to final dimensions
                    img = img.resize((final_width, final_height), Image.Resampling.LANCZOS)
                else:
                    # Scale down to final size with high quality
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                # Original square approach
                high_res_size = size * 4  # 4x resolution for better quality
                img = img.resize((high_res_size, high_res_size), Image.Resampling.LANCZOS)
                
                # Rotate the image if needed (at high resolution)
                if rotation != 0:
                    img = img.rotate(rotation, expand=True, fillcolor=(255, 255, 255, 0))
                
                # Scale down to final size with high quality
                img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            return img
        else:
            print(f"Car image not found: {image_path}")
            return None
    except Exception as e:
        print(f"Error loading car image for {driver_code}: {e}")
        return None


def calculate_direction(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate the direction angle in degrees from point 1 to point 2."""
    import math
    dx = x2 - x1
    dy = y2 - y1
    # Calculate angle in radians, then convert to degrees
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    return angle_deg


def get_race_incident_data(year: int, race: str, driver1: str, driver2: str, 
                          lap: int, start_time: str, duration: int) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Get track XY position data for two drivers during a specific part of a specific lap in the race.
    
    Args:
        year: The year of the race
        race: The name of the Grand Prix
        driver1: Three-letter driver code for first driver
        driver2: Three-letter driver code for second driver
        lap: The lap number to analyze
        start_time: Start time in format "HH:MM:SS" (race time)
        duration: Duration in seconds to capture
    
    Returns:
        Tuple of (driver1_position_data, driver2_position_data) or (None, None) if error
    """
    try:
        # Create cache directory if it doesn't exist
        cache_dir = 'f1_cache'
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            print(f"Created cache directory: {cache_dir}")
        
        # Enable caching for better performance
        fastf1.Cache.enable_cache(cache_dir)
        
        # Load the race session
        print(f"Loading race session for {year} {race}...")
        session = fastf1.get_session(year, race, 'R')
        session.load()
        
        # Debug: Show available drivers and their codes
        results = session.results
        print(f"Available drivers in session:")
        for _, driver in results.iterrows():
            print(f"  {driver['Abbreviation']} ({driver['FullName']}) - Position: {driver['Position']}")
        
        # Get position data for both drivers during the specified time period
        position_data1 = get_driver_incident_data(session, driver1, lap, start_time, duration)
        position_data2 = get_driver_incident_data(session, driver2, lap, start_time, duration)
        
        return position_data1, position_data2
        
    except Exception as e:
        print(f"Error loading session data: {e}")
        return None, None


def get_driver_incident_data(session, driver_code: str, lap: int, start_time: str, duration: int) -> Optional[pd.DataFrame]:
    """
    Get track position data (X, Y coordinates) for a specific driver during a specific time period.
    
    Args:
        session: FastF1 session object
        driver_code: Three-letter driver code
        lap: The lap number to analyze
        start_time: Start time in format "HH:MM:SS" (race time)
        duration: Duration in seconds to capture
    
    Returns:
        DataFrame with position data or None if not found
    """
    try:
        # Get the session results to find the driver
        results = session.results
        driver_result = results.loc[results['Abbreviation'] == driver_code]
        
        if driver_result.empty:
            print(f"Driver {driver_code} not found in session")
            return None
        
        # Get the driver number
        driver_number = driver_result.iloc[0]['DriverNumber']
        
        # Get position data for this driver
        position_data = session.pos_data[driver_number]
        
        if position_data.empty:
            print(f"No position data found for driver {driver_code}")
            return None
        
        # Parse the start time
        try:
            start_hour, start_min, start_sec = map(int, start_time.split(':'))
            start_seconds = start_hour * 3600 + start_min * 60 + start_sec
        except ValueError:
            print(f"Invalid start time format: {start_time}. Use HH:MM:SS format.")
            return None
        
        # Convert to timedelta for comparison
        start_timedelta = timedelta(seconds=start_seconds)
        end_timedelta = timedelta(seconds=start_seconds + duration)
        
        # Filter position data by time range
        # Convert SessionTime to seconds for easier filtering
        position_data = position_data.copy()
        position_data['SessionTimeSeconds'] = position_data['SessionTime'].dt.total_seconds()
        
        # Filter by time range
        start_seconds_total = start_timedelta.total_seconds()
        end_seconds_total = end_timedelta.total_seconds()
        
        filtered_data = position_data[
            (position_data['SessionTimeSeconds'] >= start_seconds_total) &
            (position_data['SessionTimeSeconds'] <= end_seconds_total)
        ]
        
        if filtered_data.empty:
            print(f"No position data found for {driver_code} in the specified time range")
            return None
        
        # Add driver information to the data
        filtered_data = filtered_data.copy()
        filtered_data['Driver'] = driver_code
        filtered_data['DriverNumber'] = driver_number
        filtered_data['Lap'] = lap
        filtered_data['StartTime'] = start_time
        filtered_data['Duration'] = duration
        
        print(f"Retrieved {len(filtered_data)} position data points for {driver_code} during lap {lap} from {start_time} for {duration}s")
        
        return filtered_data
        
    except Exception as e:
        print(f"Error getting incident data for driver {driver_code}: {e}")
        return None


def create_incident_animation(data1: pd.DataFrame, data2: pd.DataFrame, 
                            driver1: str, driver2: str, 
                            year: int, race: str, lap: int, start_time: str, duration: int,
                            follow: bool = False, window_size: float = 200.0,
                            gif_seconds: Optional[float] = None,
                            default_fps: int = 30, road: bool = False) -> None:
    """
    Create an animated plot showing both drivers' positions during a specific incident.
    
    Args:
        data1: Position data for first driver
        data2: Position data for second driver
        driver1: First driver code
        driver2: Second driver code
        year: Year of the race
        race: Name of the race
        lap: Lap number
        start_time: Start time of the incident
        duration: Duration of the incident
        follow: Whether to follow the cars with the camera
        window_size: Size of the follow window in meters
        gif_seconds: Target duration for the GIF in seconds
        default_fps: Default frames per second for animation
        road: If True, add realistic track surface
    """
    if len(data1) == 0 or len(data2) == 0:
        print("No position data available for animation")
        return
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Set colors based on drivers
    if driver1 == 'VER':
        color1 = '#1E41FF'  # Red Bull blue
    elif driver1 == 'HAM':
        color1 = '#00D2BE'  # Mercedes teal
    elif driver1 == 'NOR':
        color1 = '#FF8700'  # McLaren orange
    elif driver1 == 'PIA':
        color1 = '#FF8700'  # McLaren orange
    else:
        color1 = '#FFA500'  # Default orange
        
    if driver2 == 'VER':
        color2 = '#1E41FF'  # Red Bull blue
    elif driver2 == 'HAM':
        color2 = '#00D2BE'  # Mercedes teal
    elif driver2 == 'NOR':
        color2 = '#FF8700'  # McLaren orange
    elif driver2 == 'PIA':
        color2 = '#FF8700'  # McLaren orange
    else:
        color2 = '#505050'  # Default dark grey
    
    # Set markers
    marker1 = 'o'
    marker2 = 's'
    
    # Initialize car annotations (will be updated in animation)
    car1_annotation = None
    car2_annotation = None
    
    # Check if car images exist
    car1_exists = os.path.exists(f"f1-ghost-car/assets/cars/{driver1.lower()}.png")
    car2_exists = os.path.exists(f"f1-ghost-car/assets/cars/{driver2.lower()}.png")
    
    # Calculate car size based on follow mode
    if follow:
        car_size = max(30, int(window_size / 3))
    else:
        car_size = 25
    
    # Calculate line width based on car size
    line_width = max(1, 80 / 3)  # Fixed line width based on standard car size
    
    # Add road surface if requested
    if road:
        # Try to load track data first (for Hungary/Budapest and Spa)
        track_data = None
        if race.lower() in ['hungary', 'hungarian', 'budapest']:
            track_data = load_track_data('Budapest')
        elif race.lower() in ['spa', 'spa-francorchamps', 'belgium', 'belgian']:
            track_data = load_track_data('Spa')
        
        if track_data is not None:
            # Use actual track data to create road
            track_name = "Budapest" if race.lower() in ['hungary', 'hungarian', 'budapest'] else "Spa"
            print(f"Using {track_name} track data for road surface")
            create_road_from_track_data(track_data, data1, data2, ax)
            
            # Calculate proper car size based on F1 car width (2m) and track scaling
            avg_track_width = (track_data['w_tr_right_m'].mean() + track_data['w_tr_left_m'].mean())
            target_track_width_pixels = 200  # Target track width in pixels for good visualization
            pixel_density = target_track_width_pixels / avg_track_width
            f1_car_width_pixels = 2.0 * pixel_density * 2  # 2m car width in pixels, doubled for visibility
            
            if follow:
                car_size = max(int(f1_car_width_pixels), int(window_size / 20))
            else:
                car_size = int(f1_car_width_pixels)
            
            print(f"Track width: {avg_track_width:.1f}m, Car size: {car_size}px")
        else:
            # Fallback: Create thick grey road based on both driver's racing lines
            road_width = max(20, car_size * 2)
            
            # Combine both driver paths to create a road surface
            import numpy as np
            
            # Get all X,Y coordinates from both drivers
            all_x = np.concatenate([data1['X'].values, data2['X'].values])
            all_y = np.concatenate([data1['Y'].values, data2['Y'].values])
            
            # Create a convex hull or smoothed path for the road
            from scipy.spatial import ConvexHull
            
            # Remove duplicate points and sort by distance along path
            points = np.column_stack([all_x, all_y])
            unique_points = np.unique(points, axis=0)
            
            if len(unique_points) > 3:
                try:
                    # Create convex hull for road outline
                    hull = ConvexHull(unique_points)
                    hull_points = unique_points[hull.vertices]
                    
                    # Close the hull
                    hull_points = np.vstack([hull_points, hull_points[0]])
                    
                    # Plot the road as a filled polygon
                    ax.fill(hull_points[:, 0], hull_points[:, 1], 
                           color='#808080', alpha=0.6, zorder=1, label='Road Surface')
                    
                    # Add road outline
                    ax.plot(hull_points[:, 0], hull_points[:, 1], 
                           color='#606060', linewidth=road_width/10, alpha=0.8, zorder=2)
                           
                except Exception as e:
                    print(f"Could not create road surface: {e}")
                    # Fallback: create simple road from driver paths
                    ax.plot(data1['X'], data1['Y'], 
                           color='#808080', linewidth=road_width, alpha=0.6, zorder=1, label='Road Surface')
                    ax.plot(data2['X'], data2['Y'], 
                           color='#808080', linewidth=road_width, alpha=0.6, zorder=1)
    
    # Initialize empty lines
    line1, = ax.plot([], [], color=color1, linewidth=line_width, alpha=0.8, label=f'{driver1} Path')
    line2, = ax.plot([], [], color=color2, linewidth=line_width, alpha=0.8, label=f'{driver2} Path')
    
    # Create car image elements that will be updated in animation
    car1_image = None
    car2_image = None
    
    if car1_exists:
        # Create initial car image
        car1_img = load_car_image(driver1, size=car_size, rotation=0, maintain_aspect=follow)
        if car1_img:
            # Convert PIL image to numpy array for imshow
            import numpy as np
            car1_array = np.array(car1_img)
            # Get actual dimensions for proper extent
            img_height, img_width = car1_array.shape[:2]
            # Create a small image plot that we'll update
            car1_image = ax.imshow(car1_array, extent=[0, img_width, 0, img_height], 
                                 zorder=10, visible=False)
    
    if car2_exists:
        # Create initial car image
        car2_img = load_car_image(driver2, size=car_size, rotation=0, maintain_aspect=follow)
        if car2_img:
            # Convert PIL image to numpy array for imshow
            import numpy as np
            car2_array = np.array(car2_img)
            # Get actual dimensions for proper extent
            img_height, img_width = car2_array.shape[:2]
            # Create a small image plot that we'll update
            car2_image = ax.imshow(car2_array, extent=[0, img_width, 0, img_height], 
                                 zorder=10, visible=False)
    
    # Fallback markers if no car images
    point1, = ax.plot([], [], color=color1, marker=marker1, markersize=12, label=f'{driver1} Current', visible=not car1_exists)
    point2, = ax.plot([], [], color=color2, marker=marker2, markersize=12, label=f'{driver2} Current', visible=not car2_exists)
    
    # Set initial axis limits
    all_x = pd.concat([data1['X'], data2['X']])
    all_y = pd.concat([data1['Y'], data2['Y']])

    if follow:
        # Center on initial positions
        x_points = []
        y_points = []
        if len(data1) > 0:
            x_points.append(float(data1['X'].iloc[0]))
            y_points.append(float(data1['Y'].iloc[0]))
        if len(data2) > 0:
            x_points.append(float(data2['X'].iloc[0]))
            y_points.append(float(data2['Y'].iloc[0]))
        if x_points and y_points:
            cx = sum(x_points) / len(x_points)
            cy = sum(y_points) / len(y_points)
            pad = window_size * 1.2
            ax.set_xlim(cx - pad, cx + pad)
            ax.set_ylim(cy - pad, cy + pad)
        else:
            ax.set_xlim(all_x.min() - 50, all_x.max() + 50)
            ax.set_ylim(all_y.min() - 50, all_y.max() + 50)
    else:
        ax.set_xlim(all_x.min() - 50, all_x.max() + 50)
        ax.set_ylim(all_y.min() - 50, all_y.max() + 50)
    
    # Remove all UI elements for clean look
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('')
    ax.legend().set_visible(False)
    ax.grid(False)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Determine fps/interval to target desired gif duration if provided
    max_frames = max(len(data1), len(data2))
    fps = default_fps
    if gif_seconds and gif_seconds > 0:
        fps = max(1, int(round(max_frames / gif_seconds)))
    interval_ms = int(round(1000.0 / fps))

    # Animation function
    def animate(frame):
        # Update lines (show path up to current frame)
        if frame < len(data1):
            line1.set_data(data1['X'].iloc[:frame+1], data1['Y'].iloc[:frame+1])
            # Update car position or fallback marker
            if car1_image and car1_exists:
                # Calculate direction of movement
                if frame > 0:
                    direction = calculate_direction(
                        data1['X'].iloc[frame-1], data1['Y'].iloc[frame-1],
                        data1['X'].iloc[frame], data1['Y'].iloc[frame]
                    )
                    # Update car image with new rotation
                    new_car_img = load_car_image(driver1, size=car_size, rotation=direction, maintain_aspect=follow)
                    if new_car_img:
                        import numpy as np
                        car1_array = np.array(new_car_img)
                        car1_image.set_array(car1_array)
                        
                        # Update extent based on actual image dimensions
                        img_height, img_width = car1_array.shape[:2]
                        x_pos = data1['X'].iloc[frame]
                        y_pos = data1['Y'].iloc[frame]
                        car1_image.set_extent([x_pos - img_width/2, x_pos + img_width/2, 
                                             y_pos - img_height/2, y_pos + img_height/2])
                else:
                    # Update position - center the car image at the current position
                    x_pos = data1['X'].iloc[frame]
                    y_pos = data1['Y'].iloc[frame]
                    car1_image.set_extent([x_pos - car_size/2, x_pos + car_size/2, 
                                         y_pos - car_size/2, y_pos + car_size/2])
                car1_image.set_visible(True)
            else:
                point1.set_data([data1['X'].iloc[frame]], [data1['Y'].iloc[frame]])
        
        if frame < len(data2):
            line2.set_data(data2['X'].iloc[:frame+1], data2['Y'].iloc[:frame+1])
            # Update car position or fallback marker
            if car2_image and car2_exists:
                # Calculate direction of movement
                if frame > 0:
                    direction = calculate_direction(
                        data2['X'].iloc[frame-1], data2['Y'].iloc[frame-1],
                        data2['X'].iloc[frame], data2['Y'].iloc[frame]
                    )
                    # Update car image with new rotation
                    new_car_img = load_car_image(driver2, size=car_size, rotation=direction, maintain_aspect=follow)
                    if new_car_img:
                        import numpy as np
                        car2_array = np.array(new_car_img)
                        car2_image.set_array(car2_array)
                        
                        # Update extent based on actual image dimensions
                        img_height, img_width = car2_array.shape[:2]
                        x_pos = data2['X'].iloc[frame]
                        y_pos = data2['Y'].iloc[frame]
                        car2_image.set_extent([x_pos - img_width/2, x_pos + img_width/2, 
                                             y_pos - img_height/2, y_pos + img_height/2])
                else:
                    # Update position - center the car image at the current position
                    x_pos = data2['X'].iloc[frame]
                    y_pos = data2['Y'].iloc[frame]
                    car2_image.set_extent([x_pos - car_size/2, x_pos + car_size/2, 
                                         y_pos - car_size/2, y_pos + car_size/2])
                car2_image.set_visible(True)
            else:
                point2.set_data([data2['X'].iloc[frame]], [data2['Y'].iloc[frame]])

        if follow:
            # Recenter axis around current positions, ensuring both cars are always visible
            x_points = []
            y_points = []
            if frame < len(data1):
                x_points.append(float(data1['X'].iloc[frame]))
                y_points.append(float(data1['Y'].iloc[frame]))
            if frame < len(data2):
                x_points.append(float(data2['X'].iloc[frame]))
                y_points.append(float(data2['Y'].iloc[frame]))
            
            if x_points and y_points:
                # Calculate the bounding box that includes both cars
                min_x, max_x = min(x_points), max(x_points)
                min_y, max_y = min(y_points), max(y_points)
                
                # Calculate the center of the bounding box
                cx = (min_x + max_x) / 2
                cy = (min_y + max_y) / 2
                
                # Calculate the required window size to fit both cars
                required_width = max_x - min_x
                required_height = max_y - min_y
                
                # Use the larger of the required size or the specified window_size
                # Add padding to ensure cars aren't at the edge
                pad_x = max(window_size, required_width * 1.5) / 2
                pad_y = max(window_size, required_height * 1.5) / 2
                
                ax.set_xlim(cx - pad_x, cx + pad_x)
                ax.set_ylim(cy - pad_y, cy + pad_y)
        
        # Return all animated elements
        elements = [line1, line2, point1, point2]
        if car1_image:
            elements.append(car1_image)
        if car2_image:
            elements.append(car2_image)
        return elements
    
    # Create animation
    anim = animation.FuncAnimation(fig, animate, frames=max_frames, 
                                 interval=interval_ms, blit=(not follow), repeat=True)
    
    # Save animation
    filename = f"commentary_segment_{lap}_{year}_{race.replace(' ', '_')}_{driver1}_vs_{driver2}_animated.gif"
    anim.save(filename, writer='pillow', fps=fps)
    print(f"Saved incident animation: {filename}")
    
    plt.show()


def main():
    """Main function to handle command line arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description="Create animated visualizations of F1 race incidents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python race_incident_follow.py --year 2024 --race "Hungary" --driver1 "VER" --driver2 "HAM" --lap 63 --start_time "13:45:30" --duration 30
  python race_incident_follow.py --year 2024 --race "Hungary" --driver1 "VER" --driver2 "HAM" --lap 63 --start_time "13:45:30" --duration 30 --follow --road
        """
    )
    
    parser.add_argument('--year', type=int, required=True,
                       help='Year of the race (e.g., 2024)')
    parser.add_argument('--race', type=str, required=True,
                       help='Name of the Grand Prix (e.g., "Hungary", "Monaco")')
    parser.add_argument('--driver1', type=str, required=True,
                       help='Three-letter driver code for first driver (e.g., "VER", "HAM")')
    parser.add_argument('--driver2', type=str, required=True,
                       help='Three-letter driver code for second driver (e.g., "LEC", "NOR")')
    parser.add_argument('--lap', type=int, required=True,
                       help='Lap number where the incident occurred')
    parser.add_argument('--start_time', type=str, required=True,
                       help='Start time of the incident in HH:MM:SS format (race time)')
    parser.add_argument('--duration', type=int, required=True,
                       help='Duration of the incident in seconds')
    parser.add_argument('--follow', action='store_true',
                       help='Enable camera follow: keep axes centered on cars')
    parser.add_argument('--follow-window', type=float, default=200.0,
                       help='Half-size of follow window in meters (default: 200)')
    parser.add_argument('--gif-seconds', type=float,
                        help='Target GIF duration in seconds (auto-adjust fps)')
    parser.add_argument('--road', action='store_true',
                        help='Add realistic track surface based on track data')
    
    args = parser.parse_args()
    
    # Validate year
    if args.year < 2018 or args.year > 2024:
        print(f"Warning: Year {args.year} may not have complete data available.")
        print("FastF1 typically has data from 2018 onwards.")
    
    # Convert driver codes to uppercase
    driver1 = args.driver1.upper()
    driver2 = args.driver2.upper()
    
    print(f"Creating incident visualization for {driver1} vs {driver2}")
    print(f"Race: {args.year} {args.race}")
    print(f"Lap: {args.lap}, Start time: {args.start_time}, Duration: {args.duration}s")
    
    # Get incident position data
    data1, data2 = get_race_incident_data(
        args.year, args.race, driver1, driver2, 
        args.lap, args.start_time, args.duration
    )
    
    # Create animation
    if data1 is not None and data2 is not None:
        create_incident_animation(
            data1, data2, driver1, driver2, 
            args.year, args.race, args.lap, args.start_time, args.duration,
            follow=args.follow, window_size=args.follow_window,
            gif_seconds=args.gif_seconds, road=args.road
        )
    else:
        print("\n❌ Failed to retrieve incident data.")
        print("Please check:")
        print("- Year and race name are correct")
        print("- Driver codes are valid (3-letter format)")
        print("- Lap number and start time are correct")
        print("- Internet connection is available")
        sys.exit(1)


if __name__ == "__main__":
    main()




