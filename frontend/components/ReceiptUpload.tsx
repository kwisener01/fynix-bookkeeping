'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Check, AlertCircle, Loader2, Camera } from 'lucide-react';
import { api } from '@/lib/api';
import CameraCapture from './CameraCapture';
import type { ReceiptUploadResponse } from '@/types';

interface ReceiptUploadProps {
  clientId: string;
  onSuccess?: (response: ReceiptUploadResponse) => void;
}

export default function ReceiptUpload({ clientId, onSuccess }: ReceiptUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Detect if user is on mobile device
    setIsMobile(/iPhone|iPad|iPod|Android/i.test(navigator.userAgent));
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await api.uploadReceipt(file, clientId);
      setSuccess(true);

      if (onSuccess) {
        onSuccess(response);
      }

      // Reset after 2 seconds
      setTimeout(() => {
        setSuccess(false);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload receipt');
    } finally {
      setUploading(false);
    }
  }, [clientId, onSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
          ${success ? 'border-green-500 bg-green-50' : ''}
          ${error ? 'border-red-500 bg-red-50' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          {uploading && (
            <>
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
              <p className="text-sm text-gray-600">Uploading and processing receipt...</p>
            </>
          )}

          {success && !uploading && (
            <>
              <Check className="w-12 h-12 text-green-500" />
              <p className="text-sm text-green-600 font-medium">Receipt uploaded successfully!</p>
            </>
          )}

          {error && !uploading && (
            <>
              <AlertCircle className="w-12 h-12 text-red-500" />
              <p className="text-sm text-red-600">{error}</p>
            </>
          )}

          {!uploading && !success && !error && (
            <>
              <Upload className="w-12 h-12 text-gray-400" />
              <div>
                <p className="text-base font-medium text-gray-700">
                  {isDragActive ? 'Drop the receipt here' : 'Drag & drop a receipt'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to browse (JPG, PNG, PDF)
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Mobile Camera Button */}
      {isMobile && !uploading && !showCamera && (
        <button
          onClick={() => setShowCamera(true)}
          className="mt-4 w-full py-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 shadow-lg"
        >
          <Camera className="w-5 h-5" />
          Open Camera
        </button>
      )}

      {success && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800">
            ✓ Receipt processed with AI categorization and job matching
          </p>
        </div>
      )}

      {/* Camera Capture Overlay */}
      {showCamera && (
        <CameraCapture
          onCapture={(file) => {
            setShowCamera(false);
            onDrop([file]);
          }}
          onCancel={() => setShowCamera(false)}
        />
      )}
    </div>
  );
}
