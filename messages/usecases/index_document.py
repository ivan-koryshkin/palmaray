import attrs
from messages.models import TopicEmbedModel
from messages.schemas import TopicEmbedSqlFilter
from messages.usecases.protocols import ITokenize, ITopicSave

from lib.repo import GenericRepo


def split_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into ~size chars chunks, preferring paragraph/line/sentence borders, with some overlap."""
    text = text.strip()
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = max(text.rfind("\n\n", start, end), text.rfind("\n", start, end), text.rfind(". ", start, end))
            if cut > start + size // 2:
                end = cut + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


@attrs.frozen(slots=True)
class IndexResult:
    chunks: int
    truncated: bool


@attrs.frozen(kw_only=True, slots=True)
class IndexDocument:
    """Put the content of a document into the vector memory so the bot can recall it later."""

    repo: GenericRepo[TopicEmbedModel, TopicEmbedSqlFilter]
    save_topic: ITopicSave
    tokenize: ITokenize
    chunk_size: int = 1500
    overlap: int = 200
    max_chunks: int = 30

    async def __call__(self, *, user_id: int, topic_id: int, name: str, text: str) -> IndexResult:
        pieces = split_text(text, self.chunk_size, self.overlap)
        if not pieces:
            return IndexResult(chunks=0, truncated=False)

        truncated = len(pieces) > self.max_chunks
        pieces = pieces[: self.max_chunks]

        # embed everything first: a failure here must not leave half of the document in the db
        models: list[TopicEmbedModel] = []
        for i, piece in enumerate(pieces, start=1):
            chunk = f"[file: {name}, part {i}/{len(pieces)}]\n{piece}"
            models.append(
                TopicEmbedModel(
                    topic_id=topic_id,
                    user_id=user_id,
                    chunk=chunk,
                    embedding=await self.tokenize(chunk),
                    image_url=None,
                )
            )

        await self.save_topic(id=topic_id, name=f"default topic {topic_id}", user_id=user_id)
        await self.repo.create_bulk(models)
        return IndexResult(chunks=len(models), truncated=truncated)
