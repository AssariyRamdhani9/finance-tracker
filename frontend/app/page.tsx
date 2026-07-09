import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="container mx-auto px-4 py-16">
        {/* Navbar */}
        <nav className="flex justify-between items-center mb-16">
          <div className="text-2xl font-bold text-blue-600">
            💰 FinanceTracker
          </div>
          <div className="space-x-4">
            <Link 
              href="/login" 
              className="text-gray-600 hover:text-gray-900"
            >
              Login
            </Link>
            <Link 
              href="/register" 
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Mulai Gratis
            </Link>
          </div>
        </nav>

        {/* Hero */}
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Kelola Keuangan dengan AI
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Cukup foto struk, biarkan AI yang mencatat. Dapatkan insight personal 
            untuk membantu kamu mengatur pengeluaran lebih baik.
          </p>
          <div className="flex gap-4 justify-center">
            <Link 
              href="/register" 
              className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg hover:bg-blue-700 transition shadow-lg"
            >
              Mulai Sekarang
            </Link>
            <Link 
              href="/login" 
              className="bg-white text-gray-700 px-8 py-4 rounded-lg text-lg border hover:bg-gray-50 transition"
            >
              Sudah Punya Akun?
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition">
            <div className="text-4xl mb-4">📸</div>
            <h3 className="text-lg font-semibold mb-2">Scan Struk Otomatis</h3>
            <p className="text-gray-600">
              Upload foto struk, AI akan membaca dan mencatat transaksi secara otomatis.
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition">
            <div className="text-4xl mb-4">🧠</div>
            <h3 className="text-lg font-semibold mb-2">Kategorisasi Cerdas</h3>
            <p className="text-gray-600">
              Transaksi dikelompokkan otomatis ke kategori yang tepat oleh AI.
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition">
            <div className="text-4xl mb-4">💡</div>
            <h3 className="text-lg font-semibold mb-2">Insight Personal</h3>
            <p className="text-gray-600">
              Dapatkan saran finansial yang dipersonalisasi berdasarkan pola pengeluaranmu.
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}