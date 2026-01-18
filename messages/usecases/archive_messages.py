import attrs

from collections.abc import Callable

from lib.repo import GenericRepo
from messages.models import MessageModel, TopicEmbedModel
from messages.types import MessageSqlFilter, TopicEmbedSqlFilter

from datetime import datetime, timedelta

from messages.usecases.protocols import ISummarize, ITokenize

@attrs.frozen(kw_only=True, slots=True)
class ArchiveMessages:
    repo_msg: GenericRepo[MessageModel, MessageSqlFilter]
    repo_topic_embed: GenericRepo[TopicEmbedModel, TopicEmbedSqlFilter]

    tokenize: ITokenize
    summarize: ISummarize
    arhive_days: int = 3

    async def __call__(self, topic_id: int) -> None:
        messages = await self.repo_msg.list(flt={
            "date_from": timedelta(days=self.arhive_days),
            "date_to": datetime.now().date,
            "topic_id": topic_id
        })
        if len(messages) < 3:
            return
        
        topic_embedings: list[TopicEmbedModel] = []
        messages_to_summarize: list[MessageModel] = []
        for _ in range(len(messages)):
            msg = messages.pop()
            messages_to_summarize.append(msg)
            if len(messages_to_summarize) < 3:
                continue
            
            messages_content = [m.content for m in messages_to_summarize]
            text = "\n".join(messages_content)
            summarized_text = await self.summarize(text)
            summarized_text_vector = await self.tokenize(summarized_text)
            topic_embed = TopicEmbedModel(
                topic_id=topic_id,
                chunk=summarized_text,
                embedding=summarized_text_vector
            )
            topic_embedings.append(topic_embed)
        await self.repo_topic_embed.create_bulk(topic_embedings)
        await self.repo_msg.delete_bulk([m.id for m in messages])