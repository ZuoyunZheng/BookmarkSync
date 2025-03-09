# BookmarkSync
Sync bookmarks between Firefox and Chrome using Airflow. <br/>
The idea is to run Airflow in docker container to monitor Firefox and Chrome processes and sync when necessary.

## Implementation

### Bookmarks classes and BookmarkSyncOperator classes

### Firefox bookmarks
Saved in sqlite database under `~/.mozilla/firefox/<profile>/places.sqlite` with a rough schema [here](https://wiki.mozilla.org/images/0/08/Places.sqlite.schema.pdf) (not up-to-date anymore).

### Chrome bookmarks

### Airflow
Airflow triggers workflows upon Firefox and Chrome process start and stop events.
