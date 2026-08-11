"""Compatibility entrypoint for the full Streamlit dashboard."""

# Keep the documented ``streamlit run scripts/dashboard.py`` command working
# while sharing one implementation with the original lab entrypoint.
from streamlit_app import *  # noqa: F401,F403
