"""
 Process Memory Web Server Gateway Interface (WSGI) entry point.
 From root, run with:
 gunicorn wsgi:reprocess
"""
import reprocess

reprocess_api = reprocess.create_app()

if __name__ == "__main__":
    reprocess_api.run()
