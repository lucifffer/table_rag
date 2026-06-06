# table_rag
根据上传的表格PDF进行问答，注意将文件中的接口api替换为自己的api（包括MinerU服务接口和DeepSeek服务接口）
## 通过MinerU获取PDF解析结果
MinerU可以将PDF文件解析为结构化json格式，包含页眉、页脚、表格等信息。支持API调用和本地服务部署（开源协议apache 2.0）
```
python mineru_api.py
```
## 解析PDF OCR数据
针对表格内容，通过整合表头、页眉、页脚等表格信息，将表格拆分为不同的chunk。不适用RAG常见的根据token数量划分chunk的方式
```
python handle_format.py
```

## 构建数据库并回答
通过chunk构建faiss向量数据库，本项目使用bge作为embedding模型。后续问答可以不重新创建，而是直接加载数据库。
先根据用户的输入检索数据库中top_k的相似文本，之后作为prompt输入给大模型服务接口进行解答。
同时针对可能出现的无法检索有效信息、回答幻觉等问题进行限制，提升系统回答准确性
```
python main.py
```
