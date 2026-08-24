# Iris Authentication System Configuration

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
DEBUG = False

# API Configuration
API_BASE_URL = "http://localhost:5000"
API_TIMEOUT = 30

# Database Configuration
DATABASE_PATH = "../database/iris_auth.db"
TEMPLATES_PATH = "../database/templates"

# Iris Processing Configuration
IRIS_IMAGE_SIZE = 200
GABOR_SCALES = 2
GABOR_SIGMAS = 3
GABOR_ORIENTATIONS = 5
GABOR_FEATURES = 120  # scales × sigmas × orientations × 2

# Feature Extraction
STATISTICAL_FEATURES = 9
TEXTURE_FEATURES = 18
EDGE_FEATURES = 5
TOTAL_FEATURES = 152  # 120 + 9 + 18 + 5

# Similarity Matching
COSINE_WEIGHT = 0.5
EUCLIDEAN_WEIGHT = 0.3
MANHATTAN_WEIGHT = 0.2

# Decision Thresholds
VERIFICATION_THRESHOLD = 0.65  # For 1:1 matching
IDENTIFICATION_THRESHOLD = 0.60  # For 1:N matching

# Image Processing Parameters
BILATERAL_FILTER_D = 9
BILATERAL_FILTER_SIGMA = 75
CLAHE_CLIP_LIMIT = 3.0
CLAHE_TILE_SIZE = 8
MORPH_KERNEL_SIZE = 5

# Security
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # seconds

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "../logs/iris_auth.log"

# GUI Configuration
GUI_WINDOW_WIDTH = 1200
GUI_WINDOW_HEIGHT = 800
GUI_THEME_BG = "#1e1e1e"
GUI_THEME_FG = "#ffffff"
GUI_ACCENT_COLOR = "#00d4ff"
GUI_SUCCESS_COLOR = "#00ff00"
GUI_ERROR_COLOR = "#ff0000"

# Camera Configuration
CAMERA_ID = 0
CAMERA_FRAME_WIDTH = 400
CAMERA_FRAME_HEIGHT = 400
CAMERA_FPS = 30

# Performance
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
REQUEST_TIMEOUT = 60
THREAD_POOL_SIZE = 4

# Feature Export
EXPORT_FORMAT = "json"  # or "csv"
EXPORT_PATH = "../exports"
