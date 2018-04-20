class Dictionary:
    type_tablename_dict = {
        'Picture': 'picture',
        'Video': 'video',
        'Music': 'music',
        'Document': 'document',
        'Other': 'other',
        'Folder':'folder'}
    type_dict = {
        'mp3': 'Music',
        'aac': 'Music',
        'flac': 'Music',
        'ogg': 'Music',
        'wma': 'Music',
        'm4a': 'Music',
        'aiff': 'Music',
        'wav': 'Music',
        'amr': 'Music',
        'flv': 'Video',
        'ogv': 'Video',
        'avi': 'Video',
        'mp4': 'Video',
        'mpg': 'Video',
        'mpeg': 'Video',
        '3gp': 'Video',
        'mkv': 'Video',
        'ts': 'Video',
        'webm': 'Video',
        'vob': 'Video',
        'wmv': 'Video',
        'png': 'Picture',
        'jpeg': 'Picture',
        'gif': 'Picture',
        'jpg': 'Picture',
        'bmp': 'Picture',
        'svg': 'Picture',
        'webp': 'Picture',
        'psd': 'Picture',
        'tiff': 'Picture',
        'txt': 'Document',
        'pdf': 'Document',
        'doc': 'Document',
        'docx': 'Document',
        'odf': 'Document',
        'xls': 'Document',
        'xlsv': 'Document',
        'xlsx': 'Document',
        'ppt': 'Document',
        'pptx': 'Document',
        'ppsx': 'Document',
        'odp': 'Document',
        'odt': 'Document',
        'ods': 'Document',
        'md': 'Document',
        'json': 'Document',
        'csv': 'Document'}

    def getTableName(self,type):
        """ Return type's table name """

        return self.type_tablename_dict[type]

    def getFileType(self,file_extension):
        """ Return file extension's type """

        if file_extension in self.type_dict:
            return self.type_dict[file_extension]
        else:
            return 'Other'
