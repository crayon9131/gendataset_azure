import os
import glob
import pandas as pd
import asyncio
from dotenv import load_dotenv
from datasets import Dataset
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.schema import HumanMessage
from langchain_openai.chat_models import AzureChatOpenAI
from eval_azure import evaluate_metrics_in_batches

load_dotenv()  # 載入 .env 檔案

azure_model = AzureChatOpenAI() #初始化 Azure OpenAI 模型

# 設定 PDF 目錄
pdf_directory = "Question/Context/"
pdf_files = glob.glob(f"{pdf_directory}*.pdf")
if not pdf_files:
    raise FileNotFoundError("未找到任何 PDF 檔案")

def extract_full_text_from_pdf(pdf_path):
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    full_text = ""
    
    # 將所有頁面的內容合併成一個完整文本
    for doc in documents:
        full_text += doc.page_content.strip() + "\n\n"
    
    return {
        "content": full_text.strip()
    }

# 生成整個PDF的問題
async def generate_questions_for_pdf(client, pdf_text, num_questions=30):
    prompt = f"""根據以下國立臺北商業大學法規內容，產生 {num_questions} 個問題：
    法規內容：
    {pdf_text['content'][:15000]}  # 限制文本長度以防止超出模型的上下文限制
    
    請產生的問題必須符合以下要求：
    1. 問題必須直接從提供的法規內容中獲取答案，不得包含法規之外的資訊
    2. 問題應該具有實用性，即能夠幫助使用者理解和應用此法規
    3. 完全使用繁體中文，絕對不可使用簡體中文
    4. 問題的答案必須能夠從法規內容中明確找到對應條文
    
    請列出 {num_questions} 個問題：
    """
    
    response = await client.ainvoke([HumanMessage(content=prompt)])
    questions = [q.lstrip('0123456789. ').strip() for q in response.content.split("\n") if q.strip()]
    
    # 過濾重複問題並保留最多num_questions個
    unique_questions = list(set(questions))[:num_questions]
    
    return [{
        "question": q,
        "context": pdf_text["content"]
    } for q in unique_questions]

# 驗證問題
async def validate_questions(client, questions):
    validated_questions = []
    
    for q in questions:
        # 使用問題和上下文的前15000個字符以避免超出模型限制
        prompt = f"""以下是國立臺北商業大學法規內容與相關問題，請進行嚴格評估：

        法規內容：
        {q['context'][:15000]}

        問題：
        {q['question']}

        請執行以下評估任務：
        1. 請直接從法規內容中引用相關條文來回答問題
        2. 回答必須完全基於提供的法規內容，不要添加未在法規中提及的資訊
        3. 回答必須具體明確，避免模糊或一般性陳述
        4. 請標明引用的具體條款編號（如第X條第Y款）
        5. 回答格式應為：「根據《法規名稱》第X條規定，...」
        6. 若問題無法從所提供的法規內容中找到足夠資訊回答，請回答「根據提供的法規內容無法回答此問題」
        7. 必須使用繁體中文回答，絕對不可使用簡體中文
        """
        
        try:
            response = await client.ainvoke([HumanMessage(content=prompt)])
            validated_questions.append({
                "question": q["question"],
                "context": q["context"][:4000],  # 儲存時限制上下文長度
                "validation": response.content
            })
            print(f"已驗證問題: {q['question'][:50]}...")
        except Exception as e:
            print(f"驗證問題時發生錯誤: {e}")
    
    return validated_questions

# 處理單一PDF檔案
async def process_single_pdf(client, pdf_file):
    base_name = os.path.basename(pdf_file)
    print(f"處理檔案: {base_name}")
    
    # 提取整個PDF的內容
    pdf_text = extract_full_text_from_pdf(pdf_file)
    
    # 為整個PDF生成問題 
    questions = await generate_questions_for_pdf(client, pdf_text, num_questions=5)
    
    # 驗證問題
    validated_questions = await validate_questions(client, questions)
    
    # 創建 DataFrame
    df = pd.DataFrame([
        {
            "question": item["question"],
            "contexts": [item["context"]],
            "ground_truth": item["validation"],
            "metadata": f"國立臺北商業大學法規-{base_name}",
            "answer": item["validation"]
        }
        for item in validated_questions
    ])
    
    # 評估並過濾結果
    result = await evaluate_metrics_in_batches(Dataset.from_pandas(df))
    df_result = result
    
    df_filtered = df_result[(df_result["context_recall"] > 0.0) & 
                          (df_result["context_precision"] > 0.0) & 
                          (df_result["answer_relevancy"] > 0.8)]
    
    print(f"針對 {base_name} 生成了 {len(df)} 個問題，篩選出 {len(df_filtered)} 個問題")
    
    # 為單一PDF檔案保存結果
    output_dir = "Question/Generate_QA/"
    os.makedirs(output_dir, exist_ok=True)
    excel_filename = os.path.splitext(base_name)[0] + "_QA.xlsx"
    excel_path = f"{output_dir}{excel_filename}"
    
    # 產生 Excel 檔案
    df_filtered.to_excel(excel_path, index=False)
    print(f"QA結果已儲存至 Excel 檔案: {excel_path}")
    
    return df_filtered.to_dict('records')

# 主程式
async def main():
    client = azure_model()
    
    # 檢查是否有PDF檔案
    if not pdf_files:
        print(f"在 {pdf_directory} 目錄中沒有找到任何PDF檔案")
        return
    
    # 取得第一個PDF檔案進行處理
    pdf_file = pdf_files[0]
    print(f"將處理檔案: {os.path.basename(pdf_file)}")
    
    # 處理PDF檔案
    await process_single_pdf(client, pdf_file)
    print("處理完成")

if __name__ == "__main__":
    asyncio.run(main())