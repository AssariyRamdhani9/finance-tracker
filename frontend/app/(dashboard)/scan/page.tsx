'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Camera, Upload, X, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { API_BASE_URL, getAuthHeaders } from '@/lib/api'

export default function ScanReceipt() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    if (selected) {
      setFile(selected)
      setPreview(URL.createObjectURL(selected))
      setResult(null)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const dropped = e.dataTransfer.files?.[0]
    if (dropped) {
      setFile(dropped)
      setPreview(URL.createObjectURL(dropped))
      setResult(null)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleRemove = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
  }

  const handleScan = async () => {
    if (!file) return

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE_URL}/transactions/scan-receipt`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData
      })

      const data = await res.json()

      if (res.ok) {
        setResult(data)
        toast.success('Transaksi berhasil di-scan!')
        setTimeout(() => router.push('/transactions'), 3000)
      } else {
        toast.error(data.detail || 'Gagal scan struk')
      }
    } catch (error) {
      toast.error('Terjadi kesalahan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <h1 className="text-2xl font-bold mb-6">📸 Scan Struk</h1>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <p className="text-gray-500 mb-4">
          Upload foto struk belanja, AI akan membaca dan mencatat otomatis
        </p>

        {/* Upload Area */}
        {!preview ? (
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition cursor-pointer"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => document.getElementById('fileInput')?.click()}
          >
            <Camera className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-500">Drag & drop foto struk di sini</p>
            <p className="text-sm text-gray-400 mt-2">atau klik untuk pilih file</p>
            <input
              id="fileInput"
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        ) : (
          <div className="relative">
            <img
              src={preview}
              alt="Preview struk"
              className="w-full max-h-96 object-contain rounded-lg"
            />
            <button
              onClick={handleRemove}
              className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition"
            >
              <X size={20} />
            </button>
            <p className="text-sm text-gray-500 mt-2">{file?.name}</p>
          </div>
        )}

        {/* Scan Button */}
        {file && !result && (
          <button
            onClick={handleScan}
            disabled={loading}
            className="mt-6 w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Memproses...
              </>
            ) : (
              <>
                <Upload size={20} />
                Scan & Simpan
              </>
            )}
          </button>
        )}

        {/* Result */}
        {result && (
          <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-2">✅ Berhasil!</h3>
            <div className="space-y-1 text-sm">
              <p>🏪 {result.ocr.merchant || 'Tidak terdeteksi'}</p>
              <p>💰 Rp {result.ocr.total?.toLocaleString() || 0}</p>
              <p>📂 {result.category.category}</p>
              {result.category.is_ai && (
                <p className="text-xs text-green-600">🤖 Dikategorikan oleh AI</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}