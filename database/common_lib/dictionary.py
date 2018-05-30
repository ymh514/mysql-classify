class Dictionary:
    type_tablename_dict = {
        'image': 'image',
        'video': 'video',
        'music': 'music',
        'document': 'document',
        'archives': 'archives',
        'file': 'file',
        'folder': 'folder'
    }
    type_dict = {
        'mp3': 'music',
        'aac': 'music',
        'flac': 'music',
        'ogg': 'music',
        'wma': 'music',
        'm4a': 'music',
        'aiff': 'music',
        'wav': 'music',
        'amr': 'music',
        'flv': 'video',
        'ogv': 'video',
        'avi': 'video',
        'mp4': 'video',
        'mpg': 'video',
        'mpeg': 'video',
        '3gp': 'video',
        'mkv': 'video',
        'ts': 'video',
        'webm': 'video',
        'vob': 'video',
        'wmv': 'video',
        'png': 'image',
        'jpeg': 'image',
        'gif': 'image',
        'jpg': 'image',
        'bmp': 'image',
        'svg': 'image',
        'webp': 'image',
        'psd': 'image',
        'tiff': 'image',
        'txt': 'document',
        'pdf': 'document',
        'doc': 'document',
        'docx': 'document',
        'odf': 'document',
        'xls': 'document',
        'xlsv': 'document',
        'xlsx': 'document',
        'ppt': 'document',
        'pptx': 'document',
        'ppsx': 'document',
        'odp': 'document',
        'odt': 'document',
        'ods': 'document',
        'md': 'document',
        'json': 'document',
        'csv': 'document',
        'rar': 'archives',
        'zip': 'archives',
        '7z': 'archives',
        'gz': 'archives',
        'bz2': 'archives',
        'tar': 'archives',
        'dmg': 'archives',
        'tgz': 'archives',
        'xz': 'archives',
        'iso': 'archives',
        'cpio': 'archives'
    }

    def get_file_type(self, file_extension):
        """ Return file extension's type """
        return_str = ""
        if file_extension in self.type_dict:
            return_str = self.type_dict[file_extension]
        else:
            return_str = 'file'

        return return_str

    def type_create_struct(self, file_type):
        return {
            'image': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,latitude FLOAT(6) DEFAULT NULL,'
                     'longitude FLOAT(6) DEFAULT NULL,city VARCHAR(20) DEFAULT NULL,taken_time INT DEFAULT NULL,'
                     'face_id INT DEFAULT NULL,PRIMARY KEY (id));',
            'video': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,duration FLOAT(10) DEFAULT NULL,PRIMARY KEY (id));',
            'music': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,title VARCHAR(20) DEFAULT NULL,'
                     'album VARCHAR(20) DEFAULT NULL,artist VARCHAR(20) DEFAULT NULL,'
                     'duration FLOAT(10) DEFAULT NULL,samplerate INT DEFAULT NULL,PRIMARY KEY (id));',
            'document': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'archives': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'file': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'folder': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));'
        }.get(file_type)

    def type_insert_struct(self, file_type):
        return {
            'image': '(summary_id,latitude,longitude,city,taken_time)',
            'video': '(summary_id,duration)',
            'music': '(summary_id,title,album,artist,duration,samplerate)',
            'document': '(summary_id)',
            'archives': '(summary_id)',
            'file': '(summary_id)',
            'folder': '(summary_id)'
        }.get(file_type)
