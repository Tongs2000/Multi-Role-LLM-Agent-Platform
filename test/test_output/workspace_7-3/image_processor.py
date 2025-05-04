from PIL import Image, ImageFilter
import os
import uuid

class ImageProcessor:
    def __init__(self):
        self.processed_dir = 'processed'
        os.makedirs(self.processed_dir, exist_ok=True)

    def process(self, image_path, operations):
        img = Image.open(image_path)
        
        for op in operations:
            if op['type'] == 'crop':
                img = self._crop(img, op['params'])
            elif op['type'] == 'rotate':
                img = self._rotate(img, op['params'])
            elif op['type'] == 'filter':
                img = self._apply_filter(img, op['params'])
        
        output_path = os.path.join(
            self.processed_dir,
            f"{uuid.uuid4()}.{image_path.split('.')[-1]}"
        )
        img.save(output_path)
        return output_path

    def _crop(self, img, params):
        return img.crop((
            params['x'],
            params['y'],
            params['x'] + params['width'],
            params['y'] + params['height']
        ))

    def _rotate(self, img, params):
        return img.rotate(params['degrees'], expand=True)

    def _apply_filter(self, img, params):
        filter_name = params['name']
        if filter_name == 'blur':
            return img.filter(ImageFilter.BLUR)
        elif filter_name == 'contour':
            return img.filter(ImageFilter.CONTOUR)
        elif filter_name == 'sharpen':
            return img.filter(ImageFilter.SHARPEN)
        elif filter_name == 'grayscale':
            return img.convert('L')
        return img