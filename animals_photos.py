import aiohttp

class RandomPhotoAnimal:

    def __init__(self) -> None:
        self.animals = {
            'cats': "https://api.thecatapi.com/v1/images/search",
            'dogs' : "https://random.dog/woof.json",
            'foxs': "https://randomfox.ca/floof/"
        }

    async def request(self, animal: str):
        async with aiohttp.ClientSession() as session:

            animal = animal.lower().strip()
            link = self.animals.get(animal)
            if link is None:
                return

            async with session.get(link) as resposne:
                data = await resposne.json()

                match animal:
                    case 'cats':
                        return data[0]['url']

                    case 'dogs':
                        return data['url']

                    case 'foxs':
                        return data['image']


__all__ = (
    'RandomPhotoAnimal',
)