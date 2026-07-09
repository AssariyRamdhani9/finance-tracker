'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import { Sparkles, RefreshCw, Lightbulb } from 'lucide-react'
import toast from 'react-hot-toast'
import { API_BASE_URL, getAuthHeaders } from '@/lib/api'

export default function Insights() {
  const queryClient = useQueryClient()

  const { data: insights, isLoading, refetch } = useQuery({
    queryKey: ['insights'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/insights`, {
        headers: getAuthHeaders()
      })
      if (!res.ok) throw new Error('Failed to fetch insights')
      return res.json()
    }
  })

  const generateMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${API_BASE_URL}/insights/generate`, {
        method: 'POST',
        headers: getAuthHeaders()
      })
      if (!res.ok) throw new Error('Failed to generate insights')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insights'] })
      toast.success('Insight baru berhasil digenerate!')
    },
    onError: () => {
      toast.error('Gagal generate insight')
    }
  })

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Lightbulb className="text-yellow-500" size={28} />
            Insight AI
          </h1>
          <p className="text-gray-500">Dapatkan saran finansial personal dari AI</p>
        </div>
        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
        >
          <RefreshCw size={20} className={generateMutation.isPending ? 'animate-spin' : ''} />
          {generateMutation.isPending ? 'Memproses...' : 'Generate Insight'}
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="spinner"></div>
        </div>
      ) : insights && insights.length > 0 ? (
        <div className="space-y-4">
          {insights.map((insight: any) => (
            <div key={insight.id} className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition">
              <div className="flex items-start gap-3">
                <Sparkles className="text-yellow-500 flex-shrink-0 mt-1" size={24} />
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500 mb-2">
                    <span className="bg-purple-100 text-purple-600 px-2 py-0.5 rounded">
                      {insight.type === 'weekly' ? 'Mingguan' : 'Bulanan'}
                    </span>
                    <span>
                      {format(new Date(insight.period_start), 'dd MMM yyyy', { locale: id })} - 
                      {format(new Date(insight.period_end), 'dd MMM yyyy', { locale: id })}
                    </span>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    {insight.content.split('\n').map((paragraph: string, i: number) => (
                      <p key={i} className="text-gray-700 leading-relaxed">
                        {paragraph}
                      </p>
                    ))}
                  </div>
                  <p className="text-xs text-gray-400 mt-3">
                    Generated: {format(new Date(insight.generated_at), 'dd MMM yyyy HH:mm', { locale: id })}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-xl shadow-sm">
          <div className="text-6xl mb-4">🧠</div>
          <h3 className="text-lg font-semibold mb-2">Belum Ada Insight</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Mulai catat transaksi dan klik "Generate Insight" untuk mendapatkan saran 
            finansial yang dipersonalisasi dari AI.
          </p>
        </div>
      )}
    </div>
  )
}