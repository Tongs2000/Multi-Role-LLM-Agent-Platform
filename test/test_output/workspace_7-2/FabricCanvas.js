import React, { useEffect, useRef } from 'react';
import { fabric } from 'fabric';

export default function FabricCanvas({ image, activeTool, onEdit }) {
  const canvasRef = useRef(null);
  const fabricCanvasRef = useRef(null);
  const isDrawing = useRef(false);
  const startPoint = useRef(null);

  useEffect(() => {
    if (!image) return;

    fabricCanvasRef.current = new fabric.Canvas(canvasRef.current, {
      selection: false,
    });

    fabric.Image.fromURL(image, (img) => {
      fabricCanvasRef.current.add(img);
      fabricCanvasRef.current.renderAll();
    });

    // Setup event listeners for freehand drawing
    if (activeTool === 'freehand') {
      fabricCanvasRef.current.on('mouse:down', (e) => {
        isDrawing.current = true;
        startPoint.current = e.absolutePointer;
        const pointer = fabricCanvasRef.current.getPointer(e.e);
        const points = [pointer.x, pointer.y, pointer.x, pointer.y];
        const line = new fabric.Line(points, {
          strokeWidth: 2,
          stroke: 'red',
          fill: 'red',
          originX: 'center',
          originY: 'center',
        });
        fabricCanvasRef.current.add(line);
      });

      fabricCanvasRef.current.on('mouse:move', (e) => {
        if (!isDrawing.current) return;
        const pointer = fabricCanvasRef.current.getPointer(e.e);
        const line = fabricCanvasRef.current.getObjects().pop();
        line.set({ x2: pointer.x, y2: pointer.y });
        fabricCanvasRef.current.renderAll();
      });

      fabricCanvasRef.current.on('mouse:up', () => {
        isDrawing.current = false;
      });
    }

    return () => {
      fabricCanvasRef.current.dispose();
    };
  }, [image, activeTool]);

  return <canvas ref={canvasRef} width={800} height={600} />;
}