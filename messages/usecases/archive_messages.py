import asyncio
from datetime import datetime, timedelta

import attrs
from messages.models import MessageModel, TopicEmbedModel
from messages.schemas import MessageSqlFilter, TopicEmbedSqlFilter
from messages.usecases.protocols import ISummarize, ITokenize

from lib.repo import GenericRepo


@attrs.frozen(kw_only=True, slots=True)
class ArchiveMessages:
    repo_msg: GenericRepo[MessageModel, MessageSqlFilter]
    repo_topic_embed: GenericRepo[TopicEmbedModel, TopicEmbedSqlFilter]

    tokenize: ITokenize
    summarize: ISummarize
    arhive_days: int = 3

    async def __call__(self, topic_id: int) -> None:
        messages = await self.repo_msg.list(
            flt={
                "date_from": timedelta(days=self.arhive_days),
                "date_to": datetime.now().date,
                "topic_id": topic_id,
                "tokenized": False,
            }
        )
        if len(messages) < 3:
            return

        min_chunk = 3
        max_chunk = 6
        short_threshold = 100

        groups: list[list[MessageModel]] = []
        i = 0
        n = len(messages)
        while i < n:
            group: list[MessageModel] = []
            while i < n and len(group) < min_chunk:
                group.append(messages[i])
                i += 1

            while i < n and len(group) < max_chunk:
                avg_len = sum(len(m.text or "") for m in group) / len(group)
                if avg_len < short_threshold:
                    group.append(messages[i])
                    i += 1
                    continue
                break

            groups.append(group)

        async def process_group(group_msgs: list[MessageModel]) -> TopicEmbedModel:
            texts = [m.text for m in group_msgs]
            text = "\n".join(texts)
            summarized = await self.summarize(text)
            embedding = await self.tokenize(summarized)
            image_url = next((m.image_url for m in group_msgs if m.image_url), None)
            return TopicEmbedModel(topic_id=topic_id, chunk=summarized, embedding=embedding, image_url=image_url)

        tasks = [process_group(g) for g in groups if g]
        topic_embedings = await asyncio.gather(*tasks) if tasks else []
        delete_ids: list[int] = [m.id for g in groups for m in g]

        await asyncio.gather(
            self.repo_topic_embed.create_bulk(topic_embedings) if topic_embedings else asyncio.sleep(0),
            self.repo_msg.delete_bulk(delete_ids) if delete_ids else asyncio.sleep(0),
        )
