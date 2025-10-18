import os
import shutil
from config import UPLOAD_FOLDER, logger

def cleanup_files_and_folder(paths: list = None):
    """
    Deletes temporary files and optionally the upload folder.

    Args:
        paths (list, optional): List of file paths or dicts with {"path": ...} to delete.
                                If None, deletes the entire UPLOAD_FOLDER and recreates it.
    """
    try:
        if paths:
            for f in paths:
                # Handle dict input
                if isinstance(f, dict):
                    f = f.get("path")
                if f and os.path.exists(f):
                    os.remove(f)
                    logger.info(f"Deleted file: {f}")
        else:
            if os.path.exists(UPLOAD_FOLDER):
                shutil.rmtree(UPLOAD_FOLDER)
                logger.info(f"Deleted upload folder: {UPLOAD_FOLDER}")
            # Recreate folder
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            logger.info(f"Recreated upload folder: {UPLOAD_FOLDER}")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}", exc_info=True)
