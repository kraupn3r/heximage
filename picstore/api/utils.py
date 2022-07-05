import requests


def url2yield(url, chunksize=1024):
   s = requests.Session()
   response = s.get(url, stream=True)

   chunk = True
   while chunk :
      chunk = response.raw.read(chunksize)

      if not chunk:
         break

      yield chunk
