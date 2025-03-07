import os
import shutil

import sqlite3


class Bookmark:
    pass


class BookmarkSynchronizer:
    def __init__(self, profile_path, sync_url):
        """
        Initialize bookmark synchronizer with paths to browser profiles and sync directory

        :param profile_path: Full path to profile directory
        :param sync_directory: Directory where synced bookmarks will be stored
        """
        self.profile_path = profile_path
        self.sync_url = sync_url

    def extract_bookmarks(self):
        """
        Extract bookmarks from profile path
        """
        pass

    def merge_bookmarks(self):
        """
        Merge bookmarks from url, removing duplicates
        """
        pass

    def push_bookmarks(self):
        """
        Push bookmakr to url
        """
        pass


class FirefoxBookmarkSynchronizer(BookmarkSynchronizer):
    def __init__(self, profile_path, sync_url):
        super().__init__(profile_path, sync_url)

    def extract_bookmarks(self):
        """
        Extract bookmarks from Firefox profile sqlite database
        """
        # Path to Firefox's places.sqlite database
        firefox_db_path = os.path.join(self.profile_path, "places.sqlite")

        # Create a temporary copy to avoid database lock
        temp_db = os.path.join("/tmp", "places_tmp.sqlite")
        shutil.copy2(firefox_db_path, temp_db)

        # Connect to the temporary database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Extract bookmarks
        cursor.execute("""
            SELECT
                b.id,
                b.parent,
                b.title,
                b.type,
                p.url,
                b.position
            FROM moz_bookmarks AS b
            LEFT JOIN moz_places AS p ON b.fk = p.id
            ORDER BY b.parent, b.position
            LIMIT 40
        """)

        cursor.execute("""
        SELECT name
        FROM pragma_table_info('moz_bookmarks')
        UNION ALL
        SELECT name
        FROM pragma_table_info('moz_places')
        LIMIT 20;
        """)

        firefox_bookmarks = [i for i in cursor.fetchall()]
        import pdb

        pdb.set_trace()

        conn.close()
        os.remove(temp_db)

        return firefox_bookmarks

    def merge_bookmarks(self):
        """
        Merge bookmarks from url, removing duplicates and call firefox sync
        """
        pass

    def push_bookmarks(self):
        """
        Push bookmakr to url
        """
        pass


if __name__ == "__main__":
    profile_path = "/home/zheng/.mozilla/firefox/kpojqn26.default-release/"
    fbs = FirefoxBookmarkSynchronizer(profile_path, "https://example.com")
    bms = fbs.extract_bookmarks()
    import pdb

    pdb.set_trace()
    print(bms)
