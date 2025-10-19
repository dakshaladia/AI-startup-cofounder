'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { 
  DocumentIcon, 
  PhotoIcon, 
  CloudArrowUpIcon,
  XMarkIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

interface UploadedFile {
  id: string
  file: File
  type: 'pdf' | 'image' | 'text'
  status: 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  result?: any
}

export default function UploadArea() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      type: getFileType(file),
      status: 'uploading',
      progress: 0
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])

    // Simulate file processing
    newFiles.forEach((fileObj) => {
      simulateFileProcessing(fileObj.id)
    })
  }, [])

  const getFileType = (file: File): 'pdf' | 'image' | 'text' => {
    if (file.type.startsWith('image/')) return 'image'
    if (file.type === 'application/pdf') return 'pdf'
    return 'text'
  }

  const simulateFileProcessing = (fileId: string) => {
    const interval = setInterval(() => {
      setUploadedFiles(prev => 
        prev.map(file => {
          if (file.id === fileId) {
            const newProgress = Math.min(file.progress + Math.random() * 20, 100)
            const newStatus = newProgress >= 100 ? 'completed' : 'processing'
            
            if (newProgress >= 100) {
              clearInterval(interval)
              // Simulate processing result
              file.result = {
                chunks: Math.floor(Math.random() * 10) + 5,
                embeddings: Math.floor(Math.random() * 5) + 3,
                extracted_text: 'Sample extracted text...',
                metadata: {
                  pages: Math.floor(Math.random() * 20) + 1,
                  language: 'en',
                  confidence: Math.random() * 0.3 + 0.7
                }
              }
            }
            
            return { ...file, progress: newProgress, status: newStatus }
          }
          return file
        })
      )
    }, 500)
  }

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId))
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'text/*': ['.txt', '.md', '.docx']
    },
    multiple: true
  })

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <DocumentIcon className="h-8 w-8 text-red-500" />
      case 'image':
        return <PhotoIcon className="h-8 w-8 text-blue-500" />
      default:
        return <DocumentIcon className="h-8 w-8 text-gray-500" />
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'error':
        return <XMarkIcon className="h-5 w-5 text-red-500" />
      default:
        return <div className="h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-lg font-medium text-gray-900 mb-2">
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </p>
        <p className="text-gray-500">
          or click to select files (PDF, images, text documents)
        </p>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Uploaded Files ({uploadedFiles.length})
          </h3>
          
          <div className="space-y-3">
            {uploadedFiles.map((file) => (
              <motion.div
                key={file.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getFileIcon(file.type)}
                    <div>
                      <p className="font-medium text-gray-900">{file.file.name}</p>
                      <p className="text-sm text-gray-500">
                        {(file.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    {file.status === 'processing' && (
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-500">{file.progress.toFixed(0)}%</span>
                      </div>
                    )}
                    
                    {getStatusIcon(file.status)}
                    
                    <button
                      onClick={() => removeFile(file.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                
                {file.status === 'completed' && file.result && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-4 pt-4 border-t border-gray-200"
                  >
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="font-medium text-gray-900">Chunks</p>
                        <p className="text-gray-600">{file.result.chunks}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Embeddings</p>
                        <p className="text-gray-600">{file.result.embeddings}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Pages</p>
                        <p className="text-gray-600">{file.result.metadata.pages}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Confidence</p>
                        <p className="text-gray-600">
                          {(file.result.metadata.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Status */}
      {isProcessing && (
        <div className="card text-center">
          <div className="flex items-center justify-center space-x-2">
            <div className="h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-gray-600">Processing files...</span>
          </div>
        </div>
      )}
    </div>
  )
}
