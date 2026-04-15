from engine import app
import logging

# Production Server Initialization
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] PRODUCTION: %(message)s'
)

# Application Handle for WSGI (e.g., Gunicorn/Waitress)
application = app

if __name__ == "__main__":
    # Fallback to standard runner
    app.run()
