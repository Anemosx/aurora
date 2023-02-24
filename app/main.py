import os
from os.path import join
from typing import List

import uvicorn
import markdown
import mimetypes

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.chat_gpt_request import request_chatgpt

mimetypes.init()
app = FastAPI()

templates = Jinja2Templates(directory=join(os.getcwd(), "ui", "templates"))
mimetypes.add_type(join(os.getcwd(), "application", "javascript"), ".js")
app.mount(
    "/app/ui/static",
    StaticFiles(directory=join(os.getcwd(), "ui", "static")),
    name="static",
)


def openfile(filename):
    filepath = join(os.getcwd(), "ui", "pages", filename)
    with open(filepath, "r", encoding="utf-8") as input_file:
        text = input_file.read()

    html = markdown.markdown(text)
    data = {"text": html}
    return data


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = openfile("home.md")
    return templates.TemplateResponse("page.html", {"request": request, "data": data})


@app.get("/page/{page_name}", response_class=HTMLResponse)
async def show_page(request: Request, page_name: str):
    data = openfile(page_name + ".md")
    return templates.TemplateResponse("page.html", {"request": request, "data": data})


@app.post("/upload")
async def upload_file(prompt: str = Form(...), files: List[UploadFile] = File(...)):
    for file in files:
        try:
            with open(
                join(os.path.dirname(os.getcwd()), "files", "csv_test.csv"), "wb"
            ) as f:
                # with open(join(os.path.dirname(os.getcwd()), "files", file.filename), 'wb') as f:
                while contents := file.file.read(65536 * 65536):
                    f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()

    try:
        answer = request_chatgpt(prompt, "csv_test.csv")
    except Exception:
        answer = "Server Error"

    return {"prompt": prompt, "answer": answer}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
