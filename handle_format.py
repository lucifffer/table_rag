import json
from get_table_result import html_table_to_flattened

f = open('292b87ea-ef19-456b-a63a-3c82a4677fc2_content_list_v2.json', 'r', encoding='utf-8')
mineru_result = json.load(f)

# print(len(mineru_result))

all_result  = []
for num in range(len(mineru_result)):
    page_content = mineru_result[num]
    page_header = ''
    page_footer = ''
    page_num = ''
    for content in page_content:
        if content['type'] == "page_header":
            try:
                page_header += content['content']['page_header_content'][0]['content']
            except:
                continue
        elif content['type'] == "page_footer":
            try:
                page_footer += content['content']['page_footer_content'][0]['content']
            except:
                continue
        elif content['type'] == "page_number":
            try:
                page_num = content['content']['page_number_content'][0]['content']
            except:
                continue
    # print(page_header, page_footer, page_num)
    # print('-'*40)
    for content in page_content:
        if content['type'] == 'table':
            if content['content']['html'] != "":
                flattened_data = html_table_to_flattened(content['content']['html'])
                table_caption = ''
                # print(content)
                for tmp in content['content']['table_caption']:
                    table_caption += tmp['content']
                for idx, row in enumerate(flattened_data, 1):
                    print(page_header + ' ' + page_footer  + ' ' + table_caption  + ' ' + "行" + str(idx) + ':' + row + ' 页码:' + page_num)
                    all_result.append(page_header + ' ' + page_footer  + ' ' + table_caption  + ' ' + "行" + str(idx) + ':' + row + ' 页码:' + page_num)
output_file = "table_data.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(all_result))
