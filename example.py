from api import MiniGPT4
import asyncio

async def listen():

    MGPT = MiniGPT4("wss://4427e15f09c65f1071.gradio.live/queue/join",'./photo.jpg')
    await MGPT.load(print)

    x = await MGPT.ask('Привет, мой ник - ddosxd',print)
    print(x)
    
    x = await MGPT.ask('Какой у меня ник?',print)
    print(x)

asyncio.get_event_loop().run_until_complete(listen())
