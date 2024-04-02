from typing import Iterator, Optional

from langchain_core.document_loaders import BaseBlobParser
from langchain_core.document_loaders.blob_loaders import Blob
from langchain_core.documents import Document

from langchain_google_community._utils import get_client_info


class CloudVisionLoader(BaseBlobParser):
    def __init__(self, project: Optional[str] = None):
        try:
            from google.cloud import vision  # type: ignore[attr-defined]
        except ImportError as e:
            raise ImportError(
                "Cannot import google.cloud.vision, please install "
                "`pip install google-cloud-vision`."
            ) from e
        client_options = None
        if project:
            client_options = {"quota_project_id": project}
        self._client = vision.ImageAnnotatorClient(
            client_options=client_options,
            client_info=get_client_info(module="cloud-vision"),
        )

    def load(self, gcs_uri: str) -> Document:
        """Loads an image from GCS path to a Document, only the text."""
        from google.cloud import vision  # type: ignore[attr-defined]

        image = vision.Image(source=vision.ImageSource(gcs_image_uri=gcs_uri))
        text_detection_response = self._client.text_detection(image=image)
        annotations = text_detection_response.text_annotations

        if annotations:
            text = annotations[0].description
        else:
            text = ""
        return Document(page_content=text, metadata={"source": gcs_uri})

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        yield self.load(blob.path)  # type: ignore[arg-type]