"""
Main entry point for InfoInTheBox.ca
Business directory displaying company profiles
"""
from app import infointhebox_app

if __name__ == "__main__":
    infointhebox_app.run(host="0.0.0.0", port=5000, debug=True)