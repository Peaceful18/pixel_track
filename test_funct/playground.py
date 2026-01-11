import asyncio


async def say_hello(name: str, delay: float):
    print(f"Чекаємо {delay} секунд")
    await asyncio.sleep(delay)
    print(f"Файл {name} завантажено")


asyncio.run(say_hello("test.txt", 5))