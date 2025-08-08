# 📄 NTUB 法規問答生成與驗證工具

本專案透過 **Azure OpenAI + LangChain**，自動從 PDF 法規檔案中：
1. **提取全文內容**
2. **生成多個精準問題**
3. **驗證問題與法規條文的對應性**
4. **篩選高品質問答對**
5. **輸出為 Excel 方便後續使用**

---

## 🚀 功能特色
- **自動化 Q&A 生成**：針對國立臺北商業大學法規，自動產生可直接對應條文的問題  
- **問題驗證機制**：確保答案來源於法規內容，避免幻覺（Hallucination）  
- **質量評估與篩選**：透過評估指標（Recall、Precision、Answer Relevancy）過濾低品質結果  
- **全程繁體中文處理**：保證輸出內容符合繁體中文格式  
- **安全金鑰管理**：所有 API Key 與 Azure 設定透過 `.env` 檔讀取，不會在程式碼中暴露  

---

## 📦 環境需求
- Python 3.9+
- [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/) 帳號與部署
- 必要套件安裝：
  ```bash
  pip install pandas python-dotenv datasets langchain langchain_openai langchain_community pymupdf

## 🖥️ 使用方式
1. 放入 PDF 檔案將欲處理的法規 PDF 檔案放入 Question/Context/ (資料夾需自己創立可自行命名)
2. 執行程式
   ```bash
   python gendataset.py
4. 查看結果篩選後的高品質 QA 將輸出至 Question/Generate_QA/，檔名格式：
   ```bash
   <原檔名>_QA.xlsx

