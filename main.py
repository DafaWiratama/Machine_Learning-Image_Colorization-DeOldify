from deoldify import device
from deoldify.device_id import DeviceId

device.set(device=DeviceId.CPU)
from deoldify.visualize import *
import warnings

warnings.filterwarnings("ignore")

from PIL import Image
from io import BytesIO
from waitress import serve
from flask import Flask, request, Response, send_file

app = Flask(__name__)

model = get_image_colorizer(artistic=False)


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route('/', methods=['GET', 'POST'])
def colorize():
    if request.method == 'POST':
        if 'image' not in request.files:
            return Response("No 'image' Found on Request", status=300)

        render_factor = request.form.get('render_factor', 32, type=int)
        post_process = request.form.get('post_process', True, type=bool)

        image = request.files['image']
        image = Image.open(image).convert('RGB')

        image = model(image, render_factor=render_factor, post_process=post_process)

        return serve_pil_image(Image.fromarray(image))

    return """
    <form method="post" enctype="multipart/form-data">
    
        <label for="image">Image</label><br>
        <input type="file" name="image"/><br>
        
        <label for="render_factor">Render Factor</label><br>
        <input type="number" name="render_factor" value="32"/><br>
        
        <label for="post_process">Post Processing</label>
        <input type="checkbox" id="post_process" name="post_process" checked/><br>
        
        <input type="submit" value="Upload" />
    </form>
    """


serve(app, host="0.0.0.0", port=10_001)
