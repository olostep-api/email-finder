import asyncio

from src.app import async_main

if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
