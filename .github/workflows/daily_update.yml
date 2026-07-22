name: Daily Auto News Fetcher

on:
  schedule:
    # 毎日 UTC 22:00（日本時間 朝7:00）に自動実行
    - cron: '0 22 * * *'
  workflow_dispatch: # 手動実行ボタン

jobs:
  build-and-update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install google-genai

      - name: Fetch and Process News
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python fetch_news.py

      - name: Commit and Push Changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add data.json
          git commit -m "Auto-update: Daily AI/HR/Geo News [skip ci]" || exit 0
          git push
