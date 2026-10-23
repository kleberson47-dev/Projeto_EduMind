import mimetypes
import re
from pathlib import Path

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.utils._os import safe_join

RANGE_PATTERN = re.compile(r"^bytes=(\d*)-(\d*)$")
CHUNK_SIZE = 8192


def _iter_file_range(file, length):
    try:
        remaining = length
        while remaining > 0:
            data = file.read(min(CHUNK_SIZE, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data
    finally:
        file.close()


# Serve arquivos de mídia em desenvolvimento com suporte a Range, necessário para o seek de vídeos.
def serve_media_with_range(request, path):
    try:
        full_path = Path(safe_join(settings.MEDIA_ROOT, path))
    except SuspiciousFileOperation as exc:
        raise Http404("Arquivo não encontrado.") from exc

    if not full_path.is_file():
        raise Http404("Arquivo não encontrado.")

    size = full_path.stat().st_size
    content_type = mimetypes.guess_type(
        full_path.name)[0] or "application/octet-stream"
    match = RANGE_PATTERN.match(request.headers.get("Range", "").strip())

    if not match or not (match.group(1) or match.group(2)):
        response = FileResponse(open(full_path, "rb"),
                                content_type=content_type)
        response["Accept-Ranges"] = "bytes"
        return response

    if match.group(1):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else size - 1
    else:
        start = max(size - int(match.group(2)), 0)
        end = size - 1
    end = min(end, size - 1)

    if start > end:
        response = HttpResponse(status=416)
        response["Content-Range"] = f"bytes */{size}"
        return response

    length = end - start + 1
    file = open(full_path, "rb")
    file.seek(start)
    response = StreamingHttpResponse(
        _iter_file_range(file, length),
        status=206,
        content_type=content_type,
    )
    response["Content-Length"] = str(length)
    response["Content-Range"] = f"bytes {start}-{end}/{size}"
    response["Accept-Ranges"] = "bytes"
    return response
