class ImageEditor {
    constructor() {
        this.canvas = document.getElementById('image-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.currentImage = null;
        this.operations = [];
        this.selection = null;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        document.getElementById('upload-btn').addEventListener('click', () => this.handleUpload());
        document.getElementById('rotate-left').addEventListener('click', () => this.rotate(-90));
        document.getElementById('rotate-right').addEventListener('click', () => this.rotate(90));
        document.getElementById('crop-btn').addEventListener('click', () => this.applyCrop());
        document.getElementById('save-btn').addEventListener('click', () => this.saveChanges());
        
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.applyFilter(e.target.dataset.filter));
        });
        
        this.canvas.addEventListener('mousedown', (e) => this.startSelection(e));
        this.canvas.addEventListener('mousemove', (e) => this.drawSelection(e));
        this.canvas.addEventListener('mouseup', () => this.endSelection());
    }
    
    async handleUpload() {
        const fileInput = document.getElementById('file-input');
        if (!fileInput.files.length) return;
        
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (data.error) {
                alert(data.error);
                return;
            }
            
            this.loadImage(data.url);
            this.operations = [];
        } catch (error) {
            console.error('Upload failed:', error);
            alert('Upload failed');
        }
    }
    
    loadImage(url) {
        this.currentImage = new Image();
        this.currentImage.crossOrigin = 'Anonymous';
        this.currentImage.onload = () => {
            this.canvas.width = this.currentImage.width;
            this.canvas.height = this.currentImage.height;
            this.ctx.drawImage(this.currentImage, 0, 0);
        };
        this.currentImage.src = url;
    }
    
    startSelection(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.selection = {
            startX: e.clientX - rect.left,
            startY: e.clientY - rect.top,
            endX: e.clientX - rect.left,
            endY: e.clientY - rect.top
        };
    }
    
    drawSelection(e) {
        if (!this.selection) return;
        
        const rect = this.canvas.getBoundingClientRect();
        this.selection.endX = e.clientX - rect.left;
        this.selection.endY = e.clientY - rect.top;
        
        this.redrawImage();
        this.drawSelectionBox();
    }
    
    endSelection() {
        if (!this.selection) return;
        
        // Ensure positive width/height
        const x = Math.min(this.selection.startX, this.selection.endX);
        const y = Math.min(this.selection.startY, this.selection.endY);
        const width = Math.abs(this.selection.endX - this.selection.startX);
        const height = Math.abs(this.selection.endY - this.selection.startY);
        
        if (width > 10 && height > 10) {
            this.selection = { x, y, width, height };
        } else {
            this.selection = null;
            this.redrawImage();
        }
    }
    
    drawSelectionBox() {
        if (!this.selection) return;
        
        const x = Math.min(this.selection.startX, this.selection.endX);
        const y = Math.min(this.selection.startY, this.selection.endY);
        const width = Math.abs(this.selection.endX - this.selection.startX);
        const height = Math.abs(this.selection.endY - this.selection.startY);
        
        this.ctx.strokeStyle = '#FF0000';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        this.ctx.strokeRect(x, y, width, height);
        this.ctx.setLineDash([]);
    }
    
    redrawImage() {
        if (!this.currentImage) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.currentImage, 0, 0);
    }
    
    applyCrop() {
        if (!this.selection || !this.currentImage) return;
        
        this.operations.push({
            type: 'crop',
            params: {
                x: this.selection.x,
                y: this.selection.y,
                width: this.selection.width,
                height: this.selection.height
            }
        });
        
        this.processImage();
        this.selection = null;
    }
    
    rotate(degrees) {
        if (!this.currentImage) return;
        
        this.operations.push({
            type: 'rotate',
            params: { degrees }
        });
        
        this.processImage();
    }
    
    applyFilter(filterName) {
        if (!this.currentImage) return;
        
        this.operations.push({
            type: 'filter',
            params: { name: filterName }
        });
        
        this.processImage();
    }
    
    async processImage() {
        if (!this.currentImage) return;
        
        const filename = this.currentImage.src.split('/').pop();
        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: filename,
                    operations: this.operations
                })
            });
            
            const data = await response.json();
            if (data.error) {
                alert(data.error);
                return;
            }
            
            this.loadImage(data.url);
        } catch (error) {
            console.error('Processing failed:', error);
            alert('Processing failed');
        }
    }
    
    async saveChanges() {
        if (!this.currentImage) return;
        
        const link = document.createElement('a');
        link.href = this.currentImage.src;
        link.download = 'processed_' + this.currentImage.src.split('/').pop();
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Initialize the editor when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ImageEditor();
});