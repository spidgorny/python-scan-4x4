#!/usr/bin/env python3
"""
Web Interface for A4 Scanner & Photo Splitter

Flask web application with:
- Sidebar: Scan button + list of scanned files
- Middle: Full scanned image
- Right: 4 extracted photos
"""

from flask import Flask, render_template, jsonify, send_from_directory, request
from pathlib import Path
from datetime import datetime
import json
import threading

from scanners import ScannerManager, ScanSettings, ColorMode
from smart_split import split_photos_grid_smart

app = Flask(__name__)

# Directories
SCANS_DIR = Path("output/scans")
PHOTOS_DIR = Path("photos")
SCANS_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

# Global state
scan_in_progress = False
scanner_manager = None


def init_scanner():
    """Initialize scanner manager"""
    global scanner_manager
    if scanner_manager is None:
        scanner_manager = ScannerManager()
    return scanner_manager


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/scans')
def list_scans():
    """List all scanned files"""
    scans = []
    for scan_file in sorted(SCANS_DIR.glob("scan_*.png"), reverse=True):
        # Find associated photos
        basename = scan_file.stem
        photos = sorted(PHOTOS_DIR.glob(f"{basename}_photo*.png"))
        
        scans.append({
            'filename': scan_file.name,
            'path': f'/scans/{scan_file.name}',
            'timestamp': scan_file.stat().st_mtime,
            'photos': [f'/photos/{p.name}' for p in photos]
        })
    
    return jsonify(scans)


@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Trigger a new scan"""
    global scan_in_progress
    
    if scan_in_progress:
        return jsonify({'error': 'Scan already in progress'}), 409
    
    # Start scan in background thread
    thread = threading.Thread(target=perform_scan)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})


@app.route('/api/scan/status')
def scan_status():
    """Get current scan status"""
    return jsonify({
        'in_progress': scan_in_progress
    })


@app.route('/api/split', methods=['POST'])
def trigger_split():
    """Split an existing scan into photos"""
    data = request.get_json()
    scan_filename = data.get('filename')
    
    if not scan_filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    scan_path = SCANS_DIR / scan_filename
    if not scan_path.exists():
        return jsonify({'error': 'Scan file not found'}), 404
    
    try:
        # Split photos
        photos = split_photos_grid_smart(
            str(scan_path),
            str(PHOTOS_DIR)
        )
        
        return jsonify({
            'status': 'success',
            'photos': [f'/photos/{Path(p).name}' for p in photos]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def perform_scan():
    """Perform scan and split (runs in background)"""
    global scan_in_progress
    
    try:
        scan_in_progress = True
        
        # Initialize scanner
        manager = init_scanner()
        scanner_info = manager.get_preferred_scanner()
        
        if scanner_info is None:
            print("No scanner available")
            return
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scan_output = SCANS_DIR / f"scan_{timestamp}.png"
        
        # Configure settings
        settings = ScanSettings(
            resolution=300,
            color_mode=ColorMode.COLOR,
            format="PNG"
        )
        
        # Scan
        print(f"Scanning to: {scan_output}")
        result = manager.scan(scanner_info, scan_output, settings)
        
        print(f"Scan complete: {result}")
        
        # Split photos
        print("Splitting photos...")
        photos = split_photos_grid_smart(
            str(result),
            str(PHOTOS_DIR)
        )
        
        print(f"Split complete: {len(photos)} photos")
        
    except Exception as e:
        print(f"Error during scan: {e}")
    finally:
        scan_in_progress = False


@app.route('/scans/<path:filename>')
def serve_scan(filename):
    """Serve scanned images"""
    return send_from_directory(SCANS_DIR, filename)


@app.route('/photos/<path:filename>')
def serve_photo(filename):
    """Serve photo images"""
    return send_from_directory(PHOTOS_DIR, filename)


if __name__ == '__main__':
    print("=" * 60)
    print("A4 Scanner Web Interface")
    print("=" * 60)
    print()
    print("Starting server...")
    print()
    print("Open in browser: http://localhost:8090")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=8090)
