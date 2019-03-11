#!/usr/bin/env python
import hug
from hug_middleware_cors import CORSMiddleware

import subprocess
from tempfile import NamedTemporaryFile

import config

api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))

authentication = hug.authentication.basic(
    hug.authentication.verify('User1', 'mypassword'))


@hug.get('/', output=hug.output_format.file, requires=authentication)
def index():
    return "index.htm"


@hug.get('/static/{fn}', output=hug.output_format.file, requires=authentication)
def static(fn):
    return 'static/{}'.format(fn)


@hug.post('/ocr', output=hug.output_format.file, requires=authentication)
def ocr(body, response, language: "The language(s) to use for OCR"="eng"):
    if not len(body) == 1:
        raise Exception("Need exactly one file!")

    fn, content = list(body.items()).pop()

    f_out = NamedTemporaryFile(suffix='.pdf')

    with NamedTemporaryFile(suffix='.pdf', mode="wb") as f_in:
        f_in.write(content)
        f_in.flush()

        proc = subprocess.Popen(
            ['ocrmypdf', '--force-ocr', '-l', language, f_in.name, f_out.name])

        code = proc.wait()

        response.set_header('X-OCR-Exit-Code', str(code))

        print(f_out.name)

        return f_out
