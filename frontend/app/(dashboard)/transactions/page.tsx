// frontend/app/(dashboard)/transactions/page.tsx

"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { format } from "date-fns";
import { Plus, Search, Filter } from "lucide-react";
import { API_BASE_URL, getAuthHeaders } from "@/lib/api";
import ExportButton from "@/components/ExportButton";

export default function Transactions() {
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [monthFilter, setMonthFilter] = useState(format(new Date(), "yyyy-MM"));

  const {
    data: transactions,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["transactions", monthFilter],
    queryFn: async () => {
      const res = await fetch(
        `${API_BASE_URL}/transactions/month/${monthFilter}`,
        { headers: getAuthHeaders() },
      );
      if (!res.ok) throw new Error("Failed to fetch transactions");
      return res.json();
    },
  });

  const filtered = transactions?.filter((tx: any) => {
    const matchSearch =
      tx.description.toLowerCase().includes(search.toLowerCase()) ||
      tx.merchant?.toLowerCase().includes(search.toLowerCase());
    const matchCategory = !categoryFilter || tx.category === categoryFilter;
    return matchSearch && matchCategory;
  });

  const categories = [
    ...new Set(transactions?.map((tx: any) => tx.category) || []),
  ] as string[];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Transaksi</h1>
          <p className="text-gray-500">Kelola semua transaksi keuangan</p>
        </div>
        <div className="flex gap-2">
          <ExportButton month={monthFilter} />
          <Link
            href="/transactions/add"
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            <Plus size={20} />
            Tambah Transaksi
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
            size={20}
          />
          <input
            type="text"
            placeholder="Cari transaksi..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Semua Kategori</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          <input
            type="month"
            value={monthFilter}
            onChange={(e) => setMonthFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Transactions List */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="divide-y">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <div className="spinner"></div>
            </div>
          ) : filtered && filtered.length > 0 ? (
            filtered.map((tx: any) => (
              <div
                key={tx.id}
                className="p-4 flex items-center justify-between hover:bg-gray-50 transition"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{tx.description}</p>
                  <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500">
                    <span className="bg-gray-100 px-2 py-0.5 rounded">
                      {tx.category}
                    </span>
                    {tx.merchant && <span>• {tx.merchant}</span>}
                    <span>
                      • {format(new Date(tx.transaction_date), "dd/MM/yyyy")}
                    </span>
                    {tx.is_ai_categorized && (
                      <span className="bg-blue-100 text-blue-600 px-2 py-0.5 rounded text-xs">
                        AI
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <p className="font-semibold text-red-600 whitespace-nowrap">
                    -Rp {Number(tx.amount).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg mb-2">📭 Belum ada transaksi</p>
              <p className="text-sm">Mulai catat transaksi pertama kamu!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
