import google.generativeai as genai
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings
import base64

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
            self.enabled = True
        else:
            self.enabled = False
            print("⚠️ Gemini API Key not found. AI features disabled.")
    
    async def categorize_transaction(self, description: str) -> Dict[str, Any]:
        """Kategorisasi transaksi menggunakan Gemini"""
        

        if not self.enabled:
            return {
                "category": self._rule_based_categorize(description),
                "confidence": 0.5,
                "is_ai": False
            }
        
        categories = ["Makanan", "Transportasi", "Hiburan", 
                      "Tagihan", "Belanja", "Kesehatan", "Pendidikan", "Lainnya"]
        
        prompt = f"""
        Kategorikan transaksi berikut ke dalam SATU kategori dari daftar ini:
        {', '.join(categories)}
        
        Transaksi: "{description}"
        
        Jawab HANYA dengan format JSON:
        {{"category": "nama_kategori", "confidence": angka_0-1}}
        
        Contoh:
        {{"category": "Makanan", "confidence": 0.95}}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            result = json.loads(text)
            return {
                "category": result.get("category", "Lainnya"),
                "confidence": result.get("confidence", 0.7),
                "is_ai": True
            }
        except Exception as e:
            print(f"❌ AI categorization error: {e}")
            return {
                "category": self._rule_based_categorize(description),
                "confidence": 0.3,
                "is_ai": False
            }
    
    async def ocr_receipt(self, image_url: str) -> Dict[str, Any]:
        """OCR struk menggunakan Gemini Vision"""
        
        if not self.enabled:
            return {
                "merchant": "",
                "total": 0,
                "date": datetime.now().date().isoformat(),
                "items": [],
                "description": "Manual input required"
            }
        
        prompt = """
        Analisis struk belanja ini dan ekstrak informasi berikut:
        1. Nama toko/merchant
        2. Total belanja (nominal)
        3. Tanggal transaksi
        4. Daftar item yang dibeli (jika terbaca)
        5. Deskripsi singkat
        
        Kembalikan dalam format JSON:
        {
            "merchant": "nama_toko",
            "total": 75000,
            "date": "2026-07-01",
            "items": ["item1", "item2"],
            "description": "Belanja di toko X"
        }
        
        Jika ada data yang tidak terbaca, isi dengan string kosong atau 0.
        """
        
        try:

            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Failed to download image: {response.status_code}")
            
            image_data = response.content
            

            result = self.vision_model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            
            text = result.text.strip()
            

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text)
            

            return {
                "merchant": data.get("merchant", ""),
                "total": float(data.get("total", 0)),
                "date": data.get("date", datetime.now().date().isoformat()),
                "items": data.get("items", []),
                "description": data.get("description", f"Belanja di {data.get('merchant', 'toko')}")
            }
        except Exception as e:
            print(f"❌ OCR error: {e}")
            return {
                "merchant": "",
                "total": 0,
                "date": datetime.now().date().isoformat(),
                "items": [],
                "description": ""
            }
    
    async def generate_insights(self, transactions: List[Dict], budgets: List[Dict]) -> str:
        """Generate insight naratif dari data transaksi"""
        
        if not self.enabled or not transactions:
            return "Mulai catat transaksi untuk mendapatkan insight personal!"
        

        total_spent = sum(t.get("amount", 0) for t in transactions)
        categories = {}
        for t in transactions:
            cat = t.get("category", "Lainnya")
            categories[cat] = categories.get(cat, 0) + t.get("amount", 0)
        
        top_category = max(categories.items(), key=lambda x: x[1]) if categories else ("", 0)
        

        prompt = f"""
        Berdasarkan data keuangan berikut, berikan 3 insight personal dalam bahasa Indonesia:
        
        Total pengeluaran: Rp {total_spent:,.0f}
        Jumlah transaksi: {len(transactions)}
        Kategori terbesar: {top_category[0]} (Rp {top_category[1]:,.0f})
        
        Rincian per kategori:
        {json.dumps(categories, indent=2)}
        
        Budget yang dibuat:
        {json.dumps(budgets, indent=2) if budgets else "Tidak ada budget"}
        
        Berikan 3 insight:
        1. Pola pengeluaran (kategori apa yang paling besar)
        2. Rekomendasi penghematan (spesifik dan actionable)
        3. Status budget (jika ada budget)
        
        Format: 3 paragraf pendek, bahasa Indonesia yang natural dan friendly.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Insight generation error: {e}")
            return self._generate_fallback_insight(total_spent, categories, budgets)
    
    def _generate_fallback_insight(self, total: float, categories: dict, budgets: list) -> str:
        """Fallback insight tanpa AI"""
        insights = []
        

        insights.append(f"Total pengeluaran Anda bulan ini Rp {total:,.0f}.")
        

        if categories:
            top = max(categories.items(), key=lambda x: x[1])
            insights.append(f"Kategori terbesar adalah {top[0]} dengan total Rp {top[1]:,.0f}.")
        

        if budgets:
            for b in budgets:
                spent = categories.get(b.get("category", ""), 0)
                limit = b.get("monthly_limit", 0)
                if limit > 0:
                    percent = (spent / limit) * 100
                    if percent > 80:
                        insights.append(f"⚠️ Budget {b['category']} sudah {percent:.0f}%! Perhatikan pengeluaran.")
        
        return "\n".join(insights)
    
    def _rule_based_categorize(self, description: str) -> str:
        """Fallback kategorisasi rule-based"""
        keywords = {
            "Makanan": ["go food", "grab food", "warung", "resto", "mcd", "kfc", "bakso", "nasi", "makan", "minum", "kopi"],
            "Transportasi": ["grab", "gojek", "taxi", "bensin", "tol", "parkir", "ojek", "gocar", "transit"],
            "Hiburan": ["netflix", "spotify", "game", "steam", "movie", "nonton", "film", "musik"],
            "Tagihan": ["listrik", "air", "internet", "telkom", "pdam", "bpjs", "pajak"],
            "Belanja": ["toko", "supermarket", "indomaret", "alfamart", "belanja", "minimarket"],
            "Kesehatan": ["apotek", "obat", "dokter", "rumah sakit", "klinik", "kesehatan"],
            "Pendidikan": ["kursus", "buku", "seminar", "pelatihan", "les", "pendidikan"]
        }
        
        desc_lower = description.lower()
        for category, words in keywords.items():
            if any(word in desc_lower for word in words):
                return category
        
        return "Lainnya"