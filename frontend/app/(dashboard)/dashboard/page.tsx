'use client'

import { useQuery } from '@tanstack/react-query'
import ExportButton from '@/components/ExportButton'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import { 
  PieChart, 
  Pie, 
  Cell, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts'
import { API_BASE_URL, getAuthHeaders } from '@/lib/api'
import { DollarSign, CreditCard, TrendingUp } from 'lucide-react'

const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6']


interface Budget {
  id: string | number;
  category: string;
  spent: number;
  monthly_limit: number;
  percentage: number;
  is_overbudget: boolean;
}

interface Transaction {
  id: string | number;
  description: string;
  category: string;
  merchant?: string;
  transaction_date: string;
  is_ai_categorized: boolean;
  amount: number | string;
}

export default function Dashboard() {
  const currentMonth = format(new Date(), 'yyyy-MM')

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['summary', currentMonth],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/transactions/summary/${currentMonth}`, {
        headers: getAuthHeaders()
      })
      if (!res.ok) throw new Error('Failed to fetch summary')
      return res.json()
    }
  })

  const { data: transactions, isLoading: txLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/transactions?limit=10`, {
        headers: getAuthHeaders()
      })
      if (!res.ok) throw new Error('Failed to fetch transactions')
      return res.json()
    }
  })

  const { data: budgetStatus, isLoading: budgetLoading } = useQuery({
    queryKey: ['budgetStatus'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/budgets/status`, {
        headers: getAuthHeaders()
      })
      if (!res.ok) throw new Error('Failed to fetch budget status')
      return res.json()
    }
  })

  if (summaryLoading || txLoading || budgetLoading) {
    return (
      <div className="flex items-center justify-center min-h-100">
        <div className="spinner"></div>
      </div>
    )
  }

  const pieData = summary?.by_category 
    ? Object.entries(summary.by_category).map(([name, value]) => ({ name, value }))
    : []

  const totalSpent = summary?.total || 0
  const totalTransactions = summary?.count || 0

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">
          {format(new Date(), 'dd MMMM yyyy', { locale: id })}
        </p>
        <ExportButton month={currentMonth} />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <DollarSign className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Pengeluaran</p>
              <p className="text-2xl font-bold">Rp {totalSpent.toLocaleString()}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <CreditCard className="text-green-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Jumlah Transaksi</p>
              <p className="text-2xl font-bold">{totalTransactions}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Rata-rata per Transaksi</p>
              <p className="text-2xl font-bold">
                Rp {totalTransactions > 0 ? (totalSpent / totalTransactions).toLocaleString() : 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Pengeluaran per Kategori</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: { name?: string; percent?: number }) => `${name || ''} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => `Rp ${Number(value || 0).toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-center text-gray-500 py-8">Belum ada transaksi bulan ini</p>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Status Budget</h3>
          {budgetStatus && budgetStatus.length > 0 ? (
            <div className="space-y-4">
              {budgetStatus.map((budget: Budget) => (
                <div key={budget.id}>
                  <div className="flex justify-between text-sm">
                    <span>{budget.category}</span>
                    <span>
                      Rp {budget.spent.toLocaleString()} / Rp {budget.monthly_limit.toLocaleString()}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full ${
                        budget.percentage > 90 ? 'bg-red-500' :
                        budget.percentage > 70 ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(budget.percentage, 100)}%` }}
                    ></div>
                  </div>
                  {budget.is_overbudget && (
                    <p className="text-xs text-red-500 mt-1">⚠️ Melebihi budget!</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">
              Belum ada budget. Buat budget di halaman Budget.
            </p>
          )}
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold">Transaksi Terbaru</h3>
        </div>
        <div className="divide-y">
          {transactions && transactions.length > 0 ? (
            transactions.slice(0, 5).map((tx: Transaction) => (
              <div key={tx.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                <div>
                  <p className="font-medium">{tx.description}</p>
                  <p className="text-sm text-gray-500">
                    {tx.category} • {tx.merchant || '-'} • {format(new Date(tx.transaction_date), 'dd/MM/yyyy')}
                    {tx.is_ai_categorized && (
                      <span className="ml-2 text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded">
                        AI
                      </span>
                    )}
                  </p>
                </div>
                <p className="font-semibold text-red-600">
                  -Rp {Number(tx.amount).toLocaleString()}
                </p>
              </div>
            ))
          ) : (
            <p className="text-center text-gray-500 py-8">
              Belum ada transaksi. Mulai catat sekarang!
            </p>
          )}
        </div>
      </div>
    </div>
  )
}