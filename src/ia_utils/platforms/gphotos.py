from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GooglePhotos:
    READ_SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]

    def __init__(self, creds, logger):
        self.service = build(
            "photoslibrary", "v1", credentials=creds, static_discovery=False
        )
        self.logger = logger

    def list_photos(self, album_title, page_size=25):
        photos = []
        try:
            self.logger.debug(f"Finding album ID: {album_title}")
            albums_req = self.service.albums().list().execute()

            if "albums" not in albums_req:
                self.logger.warn("No albums found")
                return photos

            album = next(
                filter(lambda a: a["title"] == album_title, albums_req["albums"]), None
            )

            if album is None:
                self.logger.warn(f"Album not found: {album_title}")
                return photos

            self.logger.debug(f"Querying photos for album ID: {album['id']}")
            request = self.service.mediaItems().search(
                body={"albumId": album["id"], "pageSize": page_size}
            )

            while request is not None:
                response = request.execute()
                photos.extend(response.get("mediaItems", []))

                if "nextPageToken" in response:
                    request = self.service.mediaItems().search(
                        body={
                            "albumId": album["id"],
                            "pageSize": page_size,
                            "pageToken": response["nextPageToken"],
                        }
                    )
                else:
                    request = None

        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")

        if len(photos) <= 0:
            self.logger.warn("No photos found")
            return photos

        return photos
