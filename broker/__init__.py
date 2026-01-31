from taskiq import async_shared_broker
from taskiq_redis.redis_broker import RedisStreamBroker
from settings import settings

broker = RedisStreamBroker(url=settings.REDIS_URL)
async_shared_broker.default_broker(broker)

taskiq_app = async_shared_broker

__all__ = ("taskiq_app", "broker")