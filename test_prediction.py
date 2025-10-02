import sys
import os

# Add current directory to PYTHONPATH so Python can find 'website'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from website import create_app
import website.predict_inventory

app = create_app()


