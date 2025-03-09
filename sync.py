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
        cf. https://gist.github.com/v3l0c1r4pt0r/15ef7181b7c4546963da68bc3b31c169
        """
        # Path to Firefox's places.sqlite database
        firefox_db_path = os.path.join(self.profile_path, "places.sqlite")

        # Create a temporary copy to avoid database lock
        temp_db = os.path.join("/tmp", "places_tmp.sqlite")
        shutil.copy2(firefox_db_path, temp_db)

        # Connect to the temporary database
        conn = sqlite3.connect(temp_db)

        # get root directory contents (hopefully no bookmarks here)
        dirs = self._get_dirs(conn, 1)

        # populate root dir entries with subdirs and bookmarks (recursively)
        self._populate(conn, dirs)

        conn.close()
        os.remove(temp_db)
        with open("export.html", "w") as f:
            f.write(self._print_html(dirs))

        return dirs

    def _get_children(self, conn, parent, entry_type):
        c = conn.cursor()
        parm = (parent, entry_type)
        c.execute(
            """
            SELECT b.id as id,
            b.dateAdded as created,
            b.lastModified as modified,
            p.url as url,
            b.title as title,
            b.position as position
            FROM moz_bookmarks b
            LEFT JOIN moz_places p ON b.fk = p.id
            WHERE b.parent = ?
            AND b.type = ?
            ORDER BY b.position ASC;
            """,
            parm,
        )
        result = {}
        for t in c.fetchall():
            _id, created, modified, url, title, position = t
            if _id == 0:
                # special case - entry id 0 has id 0 as parent => avoid infinite recurrency
                continue
            result[_id] = {
                "title": title,
                "url": url,
                "created": created,
                "modified": modified,
                "position": position,
            }

        return result

    def _get_dirs(self, conn, parent):
        return self._get_children(conn, parent, 2)

    def _get_bookmarks(self, conn, parent):
        return self._get_children(conn, parent, 1)

    def _populate_bookmarks(self, conn, dirs):
        for _id in dirs:
            directory = dirs[_id]
            bookmarks = self._get_bookmarks(conn, _id)
            directory["bookmarks"] = bookmarks

    def _populate(self, conn, dirs):
        self._populate_bookmarks(conn, dirs)
        for _id in dirs:
            directory = dirs[_id]
            subdirs = self._get_dirs(conn, _id)
            directory["dirs"] = subdirs
            self._populate(conn, subdirs)

    def _print_dir(self, directory, level):
        indent_hdr = "    " * level
        indent = "    " * (level + 1)
        # begin directory
        out = """
{}<DT><H3 ADD_DATE="{:10.10}" LAST_MODIFIED="{:10.10}">{}</H3>
{}<DL><p>\n""".format(
            indent_hdr,
            str(directory["created"]),
            str(directory["modified"]),
            directory["title"],
            indent_hdr,
        )

        for d in directory["dirs"]:
            out += self._print_dir(directory["dirs"][d], level + 1)
        # print all bookmarks
        # dupa = {k: v for k, v in sorted(directory['bookmarks'].items(), key=lambda item: item['position'])}
        bookmarks_by_position = dict(
            sorted(directory["bookmarks"].items(), key=lambda item: item[1]["position"])
        )
        for i in bookmarks_by_position:
            bm = bookmarks_by_position[i]
            out += '{}<DT><A HREF="{}" ADD_DATE="{:10.10}">{}</A>\n'.format(
                indent, bm["url"], str(bm["created"]), bm["title"]
            )
        # for bm in directory['bookmarks']:
        # print(bm)

        # close directory
        out += """{}</DL><p>""".format(indent_hdr)
        return out

    # HTML functions (lots of ugly stuff)
    def _print_html(self, dirs):
        # just a comment
        output = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'none'; img-src data: *; object-src 'none'"></meta>
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks Menu</H1>
<DL><p>"""

        # TODO: print dirs
        for d in dirs:
            output += self._print_dir(dirs[d], 1)

        # close whole bookmarks object
        output += """</DL><p>"""
        return output

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
