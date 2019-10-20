import json
from io import BytesIO
from urllib import request
from urllib.error import HTTPError

import falcon
import imagehash
from PIL import Image
from PIL.Image import DecompressionBombError
from waitress import serve


class ImageHashApi:

    def on_get(self, req, resp):

        url = req.get_param('url')

        if not url:
            print('did not get url')
            resp.status = falcon.HTTP_400
            return

        img = self._generate_img_from_url(url)

        if not img:
            print('failed to get img')
            resp.status = falcon.HTTP_400
            return

        result = self._get_hashes(img)

        resp.body = json.dumps(result)


    def _generate_img_from_url(self, url):
        req = request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )

        try:
            response = request.urlopen(req, timeout=10)
            img = Image.open(BytesIO(response.read()))
        except (HTTPError, ConnectionError, OSError, DecompressionBombError, UnicodeEncodeError) as e:
            print(f'Failed to convert image {url}. {str(e)} ')
            return None

        return img if img else None

    def _get_hashes(self, img):
        result = {
            'dhash_h': None,
            'dhash_v': None,
            'ahash': None
        }
        dhash_h = imagehash.dhash(img, hash_size=16)
        dhash_v = imagehash.dhash_vertical(img, hash_size=16)
        ahash = imagehash.average_hash(img, hash_size=16)
        result['dhash_h'] = str(dhash_h)
        result['dhash_v'] = str(dhash_v)
        result['ahash'] = str(ahash)

        return result



api = falcon.API()
api.add_route('/hash', ImageHashApi())

#serve(api, host='localhost', port=8000, threads=15)