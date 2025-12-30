'use client';

import { useState, useRef, useEffect } from 'react';
import { Camera, X, Check, RotateCcw } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  onCancel: () => void;
}

export default function CameraCapture({ onCapture, onCancel }: CameraCaptureProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Start camera when component mounts
  useEffect(() => {
    startCamera();
    return () => {
      // Cleanup: stop camera when component unmounts
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Use back camera on mobile
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });

      setStream(mediaStream);
      setError(null);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setError('Unable to access camera. Please grant camera permissions.');
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to blob
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], `receipt_${Date.now()}.jpg`, { type: 'image/jpeg' });
          setCapturedFile(file);
          setPreview(canvas.toDataURL('image/jpeg'));

          // Stop camera stream
          if (stream) {
            stream.getTracks().forEach(track => track.stop());
          }
        }
      }, 'image/jpeg', 0.95);
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
    startCamera();
  };

  const handleCancel = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    onCancel();
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {!preview ? (
        // Live camera view
        <div className="flex-1 relative overflow-hidden">
          {error ? (
            // Error state
            <div className="flex items-center justify-center h-full p-6">
              <div className="text-center">
                <Camera className="w-16 h-16 text-red-500 mx-auto mb-4" />
                <p className="text-white text-lg mb-4">{error}</p>
                <button
                  onClick={startCamera}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Try Again
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Live video feed */}
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />

              {/* Hidden canvas for capture */}
              <canvas ref={canvasRef} className="hidden" />

              {/* Camera overlay UI */}
              <div className="absolute inset-0 pointer-events-none">
                {/* Capture guide frame */}
                <div className="absolute inset-0 flex items-center justify-center p-8">
                  <div className="w-full max-w-md aspect-[3/4] border-2 border-white/50 rounded-2xl"></div>
                </div>

                {/* Top instruction */}
                <div className="absolute top-8 left-0 right-0 text-center">
                  <p className="text-white text-lg font-medium bg-black/50 inline-block px-6 py-3 rounded-full">
                    Position receipt within frame
                  </p>
                </div>
              </div>

              {/* Controls */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-8">
                <div className="max-w-md mx-auto flex items-center justify-between">
                  {/* Cancel button */}
                  <button
                    onClick={handleCancel}
                    className="p-4 text-white hover:bg-white/10 rounded-full transition-colors pointer-events-auto"
                    aria-label="Cancel"
                  >
                    <X className="w-8 h-8" />
                  </button>

                  {/* Capture button */}
                  <button
                    onClick={capturePhoto}
                    className="w-20 h-20 rounded-full bg-white border-4 border-blue-500 hover:border-blue-400 transition-all shadow-2xl pointer-events-auto active:scale-95"
                    aria-label="Capture photo"
                  />

                  {/* Spacer for symmetry */}
                  <div className="w-16"></div>
                </div>
              </div>
            </>
          )}
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
              onClick={handleCancel}
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
