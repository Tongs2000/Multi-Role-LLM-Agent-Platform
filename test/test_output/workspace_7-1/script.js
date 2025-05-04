document.addEventListener('DOMContentLoaded', () => {
    const canvas = new fabric.Canvas('canvas');
    const uploadInput = document.getElementById('upload');
    const cropBtn = document.getElementById('crop');
    const rotateBtn = document.getElementById('rotate');
    const grayscaleBtn = document.getElementById('grayscale');
    const saveBtn = document.getElementById('save');

    // Upload image
    uploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                fabric.Image.fromURL(event.target.result, (img) => {
                    canvas.clear();
                    canvas.add(img);
                    canvas.renderAll();
                });
            };
            reader.readAsDataURL(file);
        }
    });

    // Crop image
    let isCropping = false;
    let cropRect = null;
    cropBtn.addEventListener('click', () => {
        const img = canvas.getObjects().find(obj => obj.type === 'image');
        if (!img) {
            alert('Please upload an image first.');
            return;
        }

        if (!isCropping) {
            isCropping = true;
            cropBtn.textContent = 'Apply Crop';
            // Add a cancel button dynamically
            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = 'Cancel';
            cancelBtn.id = 'cancelCrop';
            cancelBtn.style.marginLeft = '10px';
            document.querySelector('.controls').appendChild(cancelBtn);

            cancelBtn.addEventListener('click', () => {
                isCropping = false;
                cropBtn.textContent = 'Crop';
                canvas.remove(cropRect);
                canvas.renderAll();
                cancelBtn.remove();
            });

            cropRect = new fabric.Rect({
                left: 100,
                top: 100,
                width: 200,
                height: 200,
                fill: 'rgba(0,0,0,0.3)',
                stroke: 'black',
                strokeWidth: 2,
                selectable: true,
                hasControls: true
            });
            canvas.add(cropRect);
            canvas.setActiveObject(cropRect);
        } else {
            isCropping = false;
            cropBtn.textContent = 'Crop';
            document.getElementById('cancelCrop')?.remove();
            const activeObject = canvas.getActiveObject();
            if (activeObject && activeObject.type === 'rect') {
                const clipPath = new fabric.Rect({
                    left: activeObject.left,
                    top: activeObject.top,
                    width: activeObject.width,
                    height: activeObject.height,
                    absolutePositioned: true
                });
                img.clipPath = clipPath;
                canvas.remove(cropRect);
                canvas.renderAll();
            }
        }
    });

    // Rotate image
    rotateBtn.addEventListener('click', () => {
        const activeObject = canvas.getActiveObject();
        if (activeObject) {
            activeObject.rotate(activeObject.angle + 90);
            canvas.renderAll();
        }
    });

    // Apply grayscale filter
    grayscaleBtn.addEventListener('click', () => {
        const activeObject = canvas.getActiveObject();
        if (activeObject) {
            activeObject.filters.push(new fabric.Image.filters.Grayscale());
            activeObject.applyFilters();
            canvas.renderAll();
        }
    });

    // Brightness/Contrast filters
    const brightnessSlider = document.getElementById('brightness');
    const contrastSlider = document.getElementById('contrast');

    brightnessSlider.addEventListener('input', () => {
        const activeObject = canvas.getActiveObject();
        if (activeObject && activeObject.type === 'image') {
            activeObject.filters = activeObject.filters.filter(f => !(f instanceof fabric.Image.filters.Brightness));
            activeObject.filters.push(new fabric.Image.filters.Brightness({
                brightness: parseFloat(brightnessSlider.value)
            }));
            activeObject.applyFilters();
            canvas.renderAll();
        }
    });

    contrastSlider.addEventListener('input', () => {
        const activeObject = canvas.getActiveObject();
        if (activeObject && activeObject.type === 'image') {
            activeObject.filters = activeObject.filters.filter(f => !(f instanceof fabric.Image.filters.Contrast));
            activeObject.filters.push(new fabric.Image.filters.Contrast({
                contrast: parseFloat(contrastSlider.value)
            }));
            activeObject.applyFilters();
            canvas.renderAll();
        }
    });

    // Undo/Redo functionality
    const stateStack = [];
    let currentState = -1;

    const saveState = () => {
        // Remove future states if undo was used
        if (currentState < stateStack.length - 1) {
            stateStack.splice(currentState + 1);
        }
        // Save current canvas state
        stateStack.push(JSON.stringify(canvas));
        currentState = stateStack.length - 1;
        // Enable/disable buttons
        document.getElementById('undo').disabled = currentState <= 0;
        document.getElementById('redo').disabled = currentState >= stateStack.length - 1;
    };

    // Save state on every edit
    canvas.on('object:modified', saveState);
    uploadInput.addEventListener('change', () => {
        setTimeout(saveState, 100); // Delay to ensure image is loaded
    });

    // Undo action
    document.getElementById('undo').addEventListener('click', () => {
        if (currentState > 0) {
            currentState--;
            canvas.loadFromJSON(stateStack[currentState], () => {
                canvas.renderAll();
                document.getElementById('redo').disabled = false;
                if (currentState <= 0) {
                    document.getElementById('undo').disabled = true;
                }
            });
        }
    });

    // Redo action
    document.getElementById('redo').addEventListener('click', () => {
        if (currentState < stateStack.length - 1) {
            currentState++;
            canvas.loadFromJSON(stateStack[currentState], () => {
                canvas.renderAll();
                document.getElementById('undo').disabled = false;
                if (currentState >= stateStack.length - 1) {
                    document.getElementById('redo').disabled = true;
                }
            });
        }
    });

    // Save image
    saveBtn.addEventListener('click', () => {
        const dataURL = canvas.toDataURL({
            format: 'png',
            quality: 1
        });
        const link = document.createElement('a');
        link.download = 'edited-image.png';
        link.href = dataURL;
        link.click();
    });

    // Initialize buttons
    document.getElementById('undo').disabled = true;
    document.getElementById('redo').disabled = true;
});