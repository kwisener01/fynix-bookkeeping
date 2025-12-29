'use client';

import { useState, useRef } from 'react';
import { Camera, X, Check, RotateCcw } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  onCancel: () => void;
}

export default function CameraCapture({ onCapture, onCancel }: CameraCaptureProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCapturedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleConfirm = () => {
    if (capturedFile) {
      onCapture(capturedFile);
    }
  };

  const handleRetake = () => {
    setPreview(null);
    setCapturedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  const openCamera = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {!preview ? (
        // Camera capture screen
        <div className="flex-1 flex flex-col items-center justify-center p-6">
          <div className="text-center mb-12">
            <div className="inline-flex p-6 rounded-full bg-blue-600 mb-6">
              <Camera className="w-16 h-16 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-3">Capture Receipt</h2>
            <p className="text-gray-300 text-lg">
              Take a photo of your receipt
            </p>
          </div>

          {/* Hidden file input with camera capture */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Large capture button */}
          <button
            onClick={openCamera}
            className="w-24 h-24 rounded-full bg-white border-8 border-blue-500 hover:border-blue-400 transition-colors shadow-2xl"
            aria-label="Capture photo"
          />

          <p className="text-gray-400 text-sm mt-8">
            Tap the button to open camera
          </p>

          {/* Close button */}
          <button
            onClick={onCancel}
            className="absolute top-6 right-6 p-2 text-white hover:bg-white/10 rounded-full transition-colors"
            aria-label="Close"
          >
            <X className="w-8 h-8" />
          </button>
        </div>
      ) : (
        // Preview screen
        <div className="flex-1 flex flex-col">
          {/* Image preview */}
          <div className="flex-1 relative bg-black">
            <img
              src={preview}
              alt="Receipt preview"
              className="w-full h-full object-contain"
            />

            {/* Close button on preview */}
            <button
              onClick={onCancel}
              className="absolute top-6 right-6 p-2 text-white bg-black/50 hover:bg-black/70 rounded-full transition-colors"
              aria-label="Close"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Action buttons */}
          <div className="bg-gray-900 p-6 safe-area-bottom">
            <div className="max-w-md mx-auto flex gap-4">
              <button
                onClick={handleRetake}
                className="flex-1 py-4 bg-gray-700 text-white rounded-xl font-medium hover:bg-gray-600 transition-colors flex items-center justify-center gap-2 text-lg"
              >
                <RotateCcw className="w-5 h-5" />
                Retake
              </button>
              <button
                onClick={handleConfirm}
                className="flex-1 py-4 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 text-lg shadow-lg"
              >
                <Check className="w-5 h-5" />
                Use Photo
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
