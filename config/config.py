from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
   token: str

@dataclass
class Config:
   bot: TgBot

env: Env = Env()
env.read_env()

config = Config(
   bot = TgBot(token=env('BOT_TOKEN'))
)

print('BOT_TOKEN:', config.bot.token)