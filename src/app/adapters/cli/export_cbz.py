import asyncio
import sys
from pathlib import Path

from app.core.di import create_container
from app.core.domain.import_.cbz import ImportCBZCommand


async def main() -> None:
    path = Path(sys.argv[-1])
    container = create_container()

    async with container, container.context() as ctx:
        command = await ctx.resolve(ImportCBZCommand)
        await command.execute(archive_path=path)


if __name__ == "__main__":
    asyncio.run(main())
