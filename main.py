import os
from faiss_db import RowWiseFAISSDB
import json
from openai import OpenAI
import re

def get_db(file_path):
    f = open(file_path, 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    fs_db = RowWiseFAISSDB()
    fs_db.build_from_mineru_data(lines)


def search_query(query, faiss_db):
    search_result = faiss_db.search(query, top_k=3)
    return search_result

def answer_check(answer, source):
    # ans_num = re.findall(r"\d+\.?\d*", answer)
    ans_nums = re.findall(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b", answer)
    valid_num = [n for n in ans_nums if len(n)>1]
    # print('valid_num:', valid_num)
    num_error = True
    for part in source:
        for num in valid_num:
            if num in part['text']:
                num_error = False
    return num_error

def qa_with_check(search_result, query):
    if float(search_result[0]['similarity']) < 0.6:
        return {"answer": "未找到文档中的相关依据，无法回答该问题","source": [],"check_result": "拒答（无有效证据）","hallucination": False}
    context = "\n".join([row['text'] for row in search_result])
    prompt = "根据以下文档内容回答问题，仅使用文档中的信息，不要编造，如果文档信息中不存在直接回答不确定：\n文档内容：{0}\n问题：{1}\n答案：".format(context, query)
    # print(prompt)
    client = OpenAI(api_key="deepseek api", base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": "你是一个金融分析专家，你将根据我提供的数据进行分析回答"},
                {"role": "user", "content": prompt},
                ],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
            )
    # print(response.choices[0].message.content)
    num_error = answer_check(response.choices[0].message.content, search_result)
    if num_error:
        return {"answer": response.choices[0].message.content,"source": search_result,"check_result": "答案可能存在幻觉（无匹配证据）","hallucination": True}
    return {"answer": response.choices[0].message.content,"source": search_result,"check_result": response.choices[0].message.reasoning_content,"hallucination": False}


if __name__ == '__main__':
    get_db('./table_data.txt')
    # query = "2024年1月中信建投证券股份有限公司账面价值多少？"
    # query = "平安科技有限公司账面价值多少？"
    query_list = ["2024年1月中信建投证券股份有限公司账面价值多少？", "平安科技有限公司账面价值多少？", "中信证券股份有限公司到2025年6月30日被投资单位合计账面价值是多少？", "中信证券股份有限公司2024年12月31日为止即期偿还短期借款有多少？", "平安科技即期偿还短期借款有多少"]
    fs_db = RowWiseFAISSDB()
    fs_db.load_db()
    with open('metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    fs_db.metadata = metadata
    for query in query_list:
        print('问题：', query)
        search_result = search_query(query, fs_db)
        final_result = qa_with_check(search_result, query)
        print(final_result)
        print('-'*40)
    '''
    answer = '根据文档内容，2024年1月1日中信建投证券股份有限公司的账面价值为3,848,538,127.35元。'
    flag = answer_check(answer, search_result)
    print(flag)
    '''
