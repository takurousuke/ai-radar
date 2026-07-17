import os
import json
from datetime import datetime
import google.generativeai as genai

# Gemini API設定
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

# 検索対応モデル設定
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    tools=[{"google_search": {}}]
)

prompt = """
あなたは高度なAI・HR・地政学アナリストです。
本日時点の最新ニュースを検索し、以下の3つのカテゴリごとに1件ずつ（計3件）の重要トピックを特定してください。
また、それら3つのトピックがどう相互に関連しているか（点と線をつなぐ解説）を作成してください。

カテゴリ：
1. ai (AI技術・インフラ)
2. hr (人材・採用・組織リスキリング)
3. geo (地政学・歴史・マクロ経済)

以下の厳密なJSONフォーマットのみで出力してください。Markdownのコードブロックは不要です。

{
  "date": "YYYY/MM/DD",
  "nexusInsight": {
    "title": "本日の構造的接続（点と線をつなぐ解説）",
    "insight1": "文脈1の解説文章...",
    "insight2": "文脈2の解説文章...",
    "summary": "一言要約..."
  },
  "articles": [
    {
      "id": 1,
      "category": "ai",
      "categoryName": "💻 AI技術・インフラ",
      "title": "ニュースタイトル",
      "summary": "要約文章",
      "tag": "タグ1 / タグ2",
      "impact": "最高"
    },
    {
      "id": 2,
      "category": "hr",
      "categoryName": "👥 人材・組織リスキリング",
      "title": "ニュースタイトル",
      "summary": "要約文章",
      "tag": "タグ1 / タグ2",
      "impact": "ハイ"
    },
    {
      "id": 3,
      "category": "geo",
      "categoryName": "🌐 地政学・マクロ経済",
      "title": "ニュースタイトル",
      "summary": "要約文章",
      "tag": "タグ1 / タグ2",
      "impact": "最高"
    }
  ]
}
"""

def main():
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        new_data = json.loads(text.strip())
        
        # 既存データの読み込みと蓄積
        data_file = "data.json"
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {"insights": [], "articles": []}
            
        # 新データを先頭に追加（蓄積）
        history["insights"].insert(0, {
            "date": new_data["date"],
            "nexus": new_data["nexusInsight"]
        })
        for art in new_data["articles"]:
            art["date"] = new_data["date"]
            art["unique_id"] = len(history["articles"]) + 1
            history["articles"].insert(0, art)
            
        # 保存
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
        print("Successfully updated news data.")
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
