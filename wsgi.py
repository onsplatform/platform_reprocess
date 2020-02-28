"""
 Process Memory Web Server Gateway Interface (WSGI) entry point.
 From root, run with:
 gunicorn wsgi:reprocess
"""
import reprocess

reprocess = reprocess.create_app()

if __name__ == "__main__":
    reprocess.run()
