"""
Recording Tools - Video Recording with scrcpy
"""
import os
import subprocess
import signal
import time
from datetime import datetime
from typing import Optional

import config


# Global tracking of active recordings
_active_recordings: dict = {}


def record_video(
    device_id: Optional[str] = None,
    filename: Optional[str] = None,
    resolution: Optional[str] = None,
    bitrate: str = "8M"
) -> dict:
    """
    Start recording video using scrcpy.
    
    Args:
        device_id: Optional device ID
        filename: Optional filename for the recording
        resolution: Optional max resolution
        bitrate: Video bitrate (default: 8M)
        
    Returns:
        dict with success status and recording info
    """
    try:
        # Generate filename
        if filename:
            if not filename.endswith('.mp4'):
                filename = f"{filename}.mp4"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"
        
        filepath = os.path.join(config.VIDEOS_DIR, filename)
        recording_key = device_id or "default"
        
        # Check if already recording
        if recording_key in _active_recordings:
            return {
                "success": False,
                "error": f"Already recording for device {recording_key}. Stop first.",
                "device_id": recording_key
            }
        
        # Build scrcpy command
        cmd = ['scrcpy']
        if device_id:
            cmd.extend(['-s', device_id])
        
        cmd.extend(['--record', filepath])
        cmd.extend(['--video-bit-rate', bitrate])
        
        if resolution:
            cmd.extend(['--max-size', resolution])
        
        cmd.append('--no-playback')
        
        # Start recording process
        # Note: On Windows, we don't use preexec_fn
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        # Wait briefly to check if process started
        time.sleep(1)
        
        if process.poll() is not None:
            stderr = process.stderr.read().decode() if process.stderr else ""
            return {
                "success": False,
                "error": f"scrcpy terminated immediately: {stderr}",
                "filepath": None
            }
        
        # Store recording info
        _active_recordings[recording_key] = {
            "process": process,
            "filepath": filepath,
            "filename": filename,
            "start_time": datetime.now(),
            "device_id": recording_key
        }
        
        return {
            "success": True,
            "message": "Video recording started",
            "filepath": filepath,
            "filename": filename,
            "device_id": recording_key,
            "bitrate": bitrate,
            "process_id": process.pid
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "error": "scrcpy not found. Please install scrcpy.",
            "filepath": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start recording: {e}",
            "filepath": None
        }


def stop_video(device_id: Optional[str] = None) -> dict:
    """
    Stop the active video recording.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status and recording info
    """
    try:
        recording_key = device_id or "default"
        
        if recording_key not in _active_recordings:
            return {
                "success": False,
                "error": f"No active recording for device {recording_key}",
                "device_id": recording_key
            }
        
        recording_info = _active_recordings[recording_key]
        process = recording_info["process"]
        filepath = recording_info["filepath"]
        filename = recording_info["filename"]
        start_time = recording_info["start_time"]
        
        # Check if already terminated
        if process.poll() is not None:
            del _active_recordings[recording_key]
            return {
                "success": False,
                "error": "Recording process has already terminated",
                "filepath": filepath
            }
        
        # Terminate the process
        try:
            if os.name == 'nt':
                # Windows: send CTRL_BREAK_EVENT
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                # Unix: send SIGTERM
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        except Exception:
            pass
        
        # Cleanup
        del _active_recordings[recording_key]
        
        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Check file
        file_exists = os.path.exists(filepath)
        file_size = os.path.getsize(filepath) if file_exists else None
        
        return {
            "success": True,
            "message": "Video recording stopped",
            "filepath": filepath if file_exists else None,
            "filename": filename,
            "device_id": recording_key,
            "duration_seconds": duration,
            "file_size_bytes": file_size,
            "file_exists": file_exists
        }
        
    except Exception as e:
        # Cleanup on error
        recording_key = device_id or "default"
        if recording_key in _active_recordings:
            del _active_recordings[recording_key]
        
        return {
            "success": False,
            "error": f"Error stopping recording: {e}",
            "device_id": recording_key
        }
