from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GooglePhotos:
    READ_SCOPES = ["https://www.googleapis.com/auth/photoslibrary"]

    def __init__(self, creds, logger):
        self.service = build(
            "photoslibrary", "v1", credentials=creds, static_discovery=False
        )
        self.logger = logger

    def list_photos(self, album_id, page_size=25):
        photos = []
        fields = "nextPageToken,mediaItems(id,productUrl"
        fields += ",mediaMetadata(height,width),mimeType)"
        try:
            self.logger.debug(f"Querying photos for album ID: {album_id}")
            request = self.service.mediaItems().search(
                body={"albumId": album_id, "pageSize": page_size, "fields": fields}
            )

            while request is not None:
                response = request.execute()
                photos.extend(response.get("mediaItems", []))

                if "nextPageToken" in response:
                    request = self.service.mediaItems().search(
                        body={
                            "albumId": album_id,
                            "pageSize": page_size,
                            "pageToken": response["nextPageToken"],
                            "fields": fields,
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
