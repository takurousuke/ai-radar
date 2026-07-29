import os
import json
import re
import time
from google import genai
from google.genai import types

GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GENAI_API_KEY)

prompt = """
あなたは高度なAI・HR・地政学アナリストです。
本日時点の最新ニュースを検索し、以下の3つのカテゴリごとに1件ずつ（計3件）の重要トピックを特定してください。
また、それら3つのトピックがどう相互に関連しているか（点と線をつなぐ解説）を作成してください。

カテゴリ：
1. ai (AI技術・インフラ)
2. hr (人材・採用・組織リスキリング)
3. geo (地政学・歴史・マクロ経済)

以下の厳密なJSONフォーマットのみで出力してください。Markdownのコードブロック(```json)やその他の解説文は絶対に含めず、純粋なJSON文字列のみを出力してください。

{
  "date": "2026/07/29",
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

def generate_with_retry(max_retries=3, delay=65):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            return response
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"APIレート制限。{delay}秒待機してリトライします... ({attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise e
    raise Exception("APIの上限に達しました。時間をおいて再実行してください。")

def main():
    try:
        response = generate_with_retry()
        
        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
        
        new_data = json.loads(text.strip())
        
        data_file = "data.json"
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {"insights": [], "articles": []}
            
        history["insights"].insert(0, {
            "date": new_data["date"],
            "nexus": new_data["nexusInsight"]
        })
        for art in new_data["articles"]:
            art["date"] = new_data["date"]
            art["unique_id"] = len(history["articles"]) + 1
            history["articles"].insert(0, art)
            
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
        print("Successfully updated news data.")
    except Exception as e:
        print(f"Error during execution: {e}")
        raise e

if __name__ == "__main__":
    main()
