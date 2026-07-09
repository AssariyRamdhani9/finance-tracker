'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import { Plus, Trash2 } from 'lucide-react'
import { API_BASE_URL, getAuthHeaders } from '@/lib/api'

const CATEGORIES = [
  'Makanan', 'Transportasi', 'Hiburan', 'Tagihan',
  'Belanja', 'Kesehatan', 'Pendidikan', 'Lainnya'
]

export default function Budget() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [newBudget, setNewBudget] = useState({
    category: '',
    monthly_limit: ''
  })

  const currentMonth = format(new Date(), 'yyyy-MM')

  const { data: budgets, isLoading } = useQuery({
    queryKey: ['budgets', currentMonth],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/budgets/month/${currentMonth}`, {
        headers: getAuthHeaders()
      })
      if (!res.ok) throw new Error('Failed to fetch budgets')
      return res.json()
    }
  })

  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ['budgetStatus'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/budgets/status`, {
        headers: getAuthHeaders()
      })
      if (!res.ok) throw new Error('Failed to fetch budget status')
      return res.json()
    }
  })

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await fetch(`${API_BASE_URL}/budgets`, {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...data,
          month: `${currentMonth}-01`
        })
      })
      if (!res.ok) throw new Error('Failed to create budget')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] })
      queryClient.invalidateQueries({ queryKey: ['budgetStatus'] })
      toast.success('Budget berhasil dibuat!')
      setShowForm(false)
      setNewBudget({ category: '', monthly_limit: '' })
    },
    onError: () => {
      toast.error('Gagal membuat budget')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`${API_BASE_URL}/budgets/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      })
      if (!res.ok) throw new Error('Failed to delete budget')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] })
      queryClient.invalidateQueries({ queryKey: ['budgetStatus'] })
      toast.success('Budget dihapus')
    },
    onError: () => {
      toast.error('Gagal menghapus budget')
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newBudget.category || !newBudget.monthly_limit) {
      toast.error('Isi semua field')
      return
    }
    createMutation.mutate({
      category: newBudget.category,
      monthly_limit: parseFloat(newBudget.monthly_limit)
    })
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Budget</h1>
          <p className="text-gray-500">Atur budget per kategori</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={20} />
          {showForm ? 'Batal' : 'Buat Budget'}
        </button>
      </div>

      {/* Form Buat Budget */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <select
              required
              value={newBudget.category}
              onChange={(e) => setNewBudget({ ...newBudget, category: e.target.value })}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Pilih Kategori</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <input
              type="number"
              required
              min="0"
              placeholder="Limit (Rp)"
              value={newBudget.monthly_limit}
              onChange={(e) => setNewBudget({ ...newBudget, monthly_limit: e.target.value })}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {createMutation.isPending ? 'Menyimpan...' : 'Simpan Budget'}
            </button>
          </form>
        </div>
      )}

      {/* Budget List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {statusLoading ? (
          <div className="col-span-2 flex justify-center py-12">
            <div className="spinner"></div>
          </div>
        ) : status && status.length > 0 ? (
          status.map((budget: any) => (
            <div key={budget.id} className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold">{budget.category}</h3>
                <button
                  onClick={() => deleteMutation.mutate(budget.id)}
                  className="text-gray-400 hover:text-red-500 transition"
                >
                  <Trash2 size={18} />
                </button>
              </div>
              <div className="flex justify-between text-sm text-gray-500 mb-2">
                <span>Rp {budget.spent.toLocaleString()} terpakai</span>
                <span>Rp {budget.monthly_limit.toLocaleString()}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    budget.percentage > 90 ? 'bg-red-500' :
                    budget.percentage > 70 ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(budget.percentage, 100)}%` }}
                />
              </div>
              <div className="flex justify-between mt-2 text-sm">
                <span className="text-gray-500">
                  {budget.percentage.toFixed(0)}% terpakai
                </span>
                {budget.is_overbudget ? (
                  <span className="text-red-500 font-semibold">⚠️ Overbudget!</span>
                ) : (
                  <span className="text-gray-500">
                    Sisa Rp {budget.remaining.toLocaleString()}
                  </span>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-2 text-center py-12 text-gray-500 bg-white rounded-xl">
            <p className="text-lg mb-2">📊 Belum ada budget</p>
            <p className="text-sm">Buat budget untuk mulai mengontrol pengeluaran</p>
          </div>
        )}
      </div>
    </div>
  )
}