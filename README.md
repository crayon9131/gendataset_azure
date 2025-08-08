# NTUB 法規問答生成與驗證工具
本專案透過 Azure OpenAI + LangChain，自動從 PDF 法規檔案中：

提取全文內容

生成多個精準問題

驗證問題與法規條文的對應性

篩選高品質問答對

輸出為 Excel 方便後續使用

📦 環境需求
Python 3.9+

Azure OpenAI 帳號與部署

以下 Python 套件：
pip install pandas python-dotenv datasets langchain langchain_openai langchain_community pymupdf

🖥️ 使用方式
放入 PDF 檔案
將欲處理的法規 PDF 檔案放入 Question/Context/ 資料夾

執行程式
python gendataset_azure.py
查看結果
篩選後的高品質 QA 將輸出至 Question/Generate_QA/，檔名格式：

<原檔名>_QA.xlsx

📊 評估指標
生成的問答對會透過 eval_azure.py 進行批次評估：

Context Recall > 0.0

Context Precision > 0.0

Answer Relevancy > 0.8
符合條件的問答對才會保留。

⚠️ 注意事項
本專案為特定法規問答生成的範例，若用於其他內容，需調整 Prompt 與模型參數

Azure OpenAI 模型的輸出內容長度有限制，長文處理時會截斷（目前設定為 15000 字元）
