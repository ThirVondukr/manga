from pathlib import PurePath

from app.core.domain.images.services import ImageService
from app.core.storage import FileUpload
from app.settings import ImageSettings
from tests.utils import TestFileStorage, create_dummy_image_file


async def test_upload_scr_set(
    s3_mock: TestFileStorage,
    image_service: ImageService,
    image_settings: ImageSettings,
) -> None:
    size = max(image_settings.src_set) + 100
    image_file = create_dummy_image_file(size=(size, size))

    path = PurePath("test/1.png")
    upload = FileUpload(
        file=image_file,
        path=path,
    )
    async with image_service.upload_src_set(upload=upload) as images:
        pass
    assert len(images) == len(image_settings.src_set) + 1

    for image in images:
        assert image.path.as_posix() in s3_mock.files
        if image.width != size:
            assert image.path.stem == f"{path.stem}-{image.width}w"

    for width in (*image_settings.src_set, size):
        assert width in (img.width for img in images)
