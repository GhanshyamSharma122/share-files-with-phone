# Wi-Fi File Share Application Configuration
import os

# Base directory (where the app is located)
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Shared files folder
SHARED_FOLDER = os.path.join(BASE_DIR, "shared_files")
os.makedirs(SHARED_FOLDER, exist_ok=True)

# Server configuration
HOST = "0.0.0.0"
PORT = 5000

# Upload limits
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024 * 500  # 500GB limit

# File extension categories
FILE_CATEGORIES = {
    'image': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico'},
    'video': {'.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v'},
    'audio': {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.wma'},
    'document': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.csv', '.ppt', '.pptx'},
    'archive': {'.zip', '.rar', '.7z', '.tar', '.gz'},
    'code': {'.py', '.js', '.html', '.css', '.json', '.xml', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs'},
}

# File icons mapping
FILE_ICONS = {
    # Images
    '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.webp': '🖼️', 
    '.svg': '🖼️', '.bmp': '🖼️', '.ico': '🖼️',
    # Videos
    '.mp4': '🎬', '.webm': '🎬', '.mkv': '🎬', '.avi': '🎬', '.mov': '🎬', 
    '.flv': '🎬', '.wmv': '🎬', '.m4v': '🎬',
    # Audio
    '.mp3': '🎵', '.wav': '🎵', '.ogg': '🎵', '.flac': '🎵', '.aac': '🎵', 
    '.m4a': '🎵', '.wma': '🎵',
    # Documents
    '.pdf': '📄', '.doc': '📝', '.docx': '📝', '.txt': '📃', '.rtf': '📝',
    '.xls': '📊', '.xlsx': '📊', '.csv': '📊',
    '.ppt': '📽️', '.pptx': '📽️',
    # Code
    '.py': '🐍', '.js': '💛', '.html': '🌐', '.css': '🎨', '.json': '📋', 
    '.xml': '📋', '.java': '☕', '.cpp': '⚙️', '.c': '⚙️', '.h': '⚙️', 
    '.cs': '💜', '.go': '🐹', '.rs': '🦀',
    # Archives
    '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦', '.gz': '📦',
    # Executables
    '.exe': '⚡', '.msi': '⚡', '.app': '⚡', '.dmg': '💿',
    # Others
    '.apk': '📱', '.ipa': '📱',
}

# Previewable file extensions
PREVIEWABLE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
    '.mp4', '.webm',
    '.mp3', '.wav', '.ogg',
    '.pdf'
}
