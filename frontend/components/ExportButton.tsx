'use client'

import { useState } from 'react'
import { Download, FileSpreadsheet, FileText, FileBarChart } from 'lucide-react'
import { getAuthHeaders, API_BASE_URL } from '@/lib/api'
import toast from 'react-hot-toast'

interface ExportButtonProps {
  month?: string
}

export default function ExportButton({ month }: ExportButtonProps) {
  const [loading, setLoading] = useState<'csv' | 'excel' | 'pdf' | 'summary' | null>(null)
  const [showDropdown, setShowDropdown] = useState(false)

  const handleExport = async (format: 'csv' | 'excel' | 'pdf' | 'summary') => {
    setLoading(format)
    setShowDropdown(false)

    try {
      const url = `${API_BASE_URL}/export/${format}${month ? `?month=${month}` : ''}`
      
      const response = await fetch(url, {
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Export failed')
      }

      // Download file
      const blob = await response.blob()
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = `transactions_${new Date().toISOString().split('T')[0]}`
      
      if (format === 'csv') filename += '.csv'
      else if (format === 'excel' || format === 'summary') filename += '.xlsx'
      else if (format === 'pdf') filename += '.pdf'
      
      const url_blob = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url_blob
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url_blob)
      document.body.removeChild(a)

      toast.success(`Export ${format.toUpperCase()} berhasil!`)
    } catch (error) {
      toast.error('Gagal export data')
      console.error('Export error:', error)
    } finally {
      setLoading(null)
    }
  }

  const exportOptions = [
    { id: 'csv', label: 'CSV', icon: FileText, desc: 'Kompatibel dengan Excel' },
    { id: 'excel', label: 'Excel', icon: FileSpreadsheet, desc: 'Format .xlsx' },
    { id: 'pdf', label: 'PDF', icon: Download, desc: 'Laporan siap cetak' },
    { id: 'summary', label: 'Summary + Statistik', icon: FileBarChart, desc: 'Excel dengan analisis' },
  ]

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
      >
        <Download size={20} />
        Export Data
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-lg border z-50 py-2">
          <div className="px-4 py-2 border-b">
            <p className="text-sm font-semibold text-gray-700">Export Transaksi</p>
            <p className="text-xs text-gray-500">Pilih format yang diinginkan</p>
          </div>
          
          {exportOptions.map((option) => {
            const Icon = option.icon
            const isLoading = loading === option.id
            return (
              <button
                key={option.id}
                onClick={() => handleExport(option.id as any)}
                disabled={!!loading}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition disabled:opacity-50"
              >
                <div className="p-2 bg-gray-100 rounded-lg">
                  <Icon size={18} className="text-gray-600" />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium text-gray-700">{option.label}</p>
                  <p className="text-xs text-gray-500">{option.desc}</p>
                </div>
                {isLoading && (
                  <div className="spinner w-4 h-4"></div>
                )}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}