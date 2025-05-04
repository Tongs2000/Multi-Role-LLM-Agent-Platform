import os
from werkzeug.utils import secure_filename

class Storage:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def save(self, file, filename):
        filename = secure_filename(filename)
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        return filepath

    def get_path(self, filename):
        return os.path.join(self.upload_folder, filename)

    def get_url(self, filename):
        return f"/uploads/{filename}"