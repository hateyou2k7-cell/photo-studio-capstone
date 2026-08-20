import os
import uuid
from typing import List, Optional
from werkzeug.utils import secure_filename
from config import Config
from domain.models.space_image import SpaceImage
from domain.models.ispace_image_repository import ISpaceImageRepository

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}


class SpaceImageService:
    def __init__(self, repository: ISpaceImageRepository):
        self.repository = repository

    def _upload_folder(self) -> str:
        folder = getattr(Config, 'UPLOAD_FOLDER', os.path.join(os.getcwd(), 'uploads'))
        os.makedirs(folder, exist_ok=True)
        return folder

    def _is_allowed(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def save_upload(self, file) -> str:
        if not file or file.filename == '':
            raise ValueError('Empty file')
        if not self._is_allowed(file.filename):
            raise ValueError('File type not allowed')
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file.save(os.path.join(self._upload_folder(), filename))
        return f"/uploads/{filename}"

    def add_images(self, space_id: int, files: List) -> List[SpaceImage]:
        created = []
        for index, file in enumerate(files):
            url = self.save_upload(file)
            existing = self.repository.list(space_id)
            is_primary = len(existing) == 0 and index == 0
            sort_order = len(existing) + index
            image = SpaceImage(id=None, space_id=space_id, url=url,
                               is_primary=is_primary, sort_order=sort_order, created_at=None)
            created.append(self.repository.add(image))
        return created

    def list_images(self, space_id: int) -> List[SpaceImage]:
        return self.repository.list(space_id)

    def delete_image(self, space_id: int, image_id: int) -> None:
        image = self.repository.get_by_id(image_id)
        if not image or image.space_id != space_id:
            raise ValueError('Image not found')
        url = image.url
        self.repository.delete(image_id)
        if url and url.startswith('/uploads/'):
            path = os.path.join(self._upload_folder(), os.path.basename(url))
            if os.path.exists(path):
                os.remove(path)

    def set_primary(self, space_id: int, image_id: int) -> Optional[SpaceImage]:
        existing = self.repository.get_by_id(image_id)
        if not existing or existing.space_id != space_id:
            raise ValueError('Image not found')
        self.repository.clear_primary(space_id)
        image = self.repository.get_by_id(image_id)
        image.is_primary = True
        return self.repository.update(image)