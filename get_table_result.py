from bs4 import BeautifulSoup
from itertools import zip_longest

def html_table_to_flattened(html_content: str) -> list[str]:
    """
    将HTML表格转换为单元格级扁平化格式
    格式示例: "被投资单位名称: 张三, 2024年12月31日账面价值: 100.00, ..."
    
    Args:
        html_content: 包含单个表格的HTML字符串
        
    Returns:
        扁平化后的行字符串列表
    """
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    if not table:
        raise ValueError("HTML内容中未找到<table>标签")
    
    rows = table.find_all('tr')
    if len(rows) == 0:
        raise ValueError("表格中没有任何行数据")
    
    # 提取表头（第一行）
    headers = [td.get_text(strip=True) for td in rows[0].find_all('td')]
    
    # 处理所有数据行
    flattened_rows = []
    for row in rows[1:]:  # 跳过表头行
        # 提取单元格文本并去除首尾空白
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        
        # 统一空值表示：将空字符串转换为"-"（与原表格保持一致）
        cells = [cell if cell else "-" for cell in cells]
        
        # 配对表头和单元格值，自动处理行列数不匹配的情况
        row_pairs = []
        for header, cell in zip_longest(headers, cells, fillvalue="-"):
            if cell.strip() == '合计' or cell.strip() == '合计:' or cell.strip() == '合计：' or cell.strip() == '小计' or cell.strip() == '小计:' or cell.strip() == '小计：':
                row_pairs.append(f"{header}{cell}")
            else:
                row_pairs.append(f"{header}: {cell}")
        
        # 拼接为最终的扁平化字符串
        flattened_row = ", ".join(row_pairs)
        flattened_rows.append(flattened_row)
    
    return flattened_rows

# ------------------- 主程序执行 -------------------
if __name__ == "__main__":
    # 您提供的HTML表格内容
    html_input = """
    <table><tr><td>被投资单位名称</td><td>2024年12月31日账面价值</td><td>本期增加</td><td>本期减少</td><td>2025年6月30日账面价值</td><td>减值准备</td></tr><tr><td>权益法:</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>合营企业:</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Sino-OceanLandLogisticsInvestmentManagementLimited</td><td>7.19</td><td>-</td><td>0.03</td><td>7.16</td><td>-</td></tr><tr><td>CSOBORFundGPLimited</td><td>352.48</td><td>-</td><td>1.70</td><td>350.78</td><td>-</td></tr><tr><td>BrightLeeCapitalLimited</td><td>345.30</td><td>-</td><td>1.68</td><td>343.62</td><td>-</td></tr><tr><td>DoubleNitrogenFundGP,Limited</td><td>345.28</td><td>-</td><td>1.66</td><td>343.62</td><td>-</td></tr><tr><td>SunriseCapitalHoldingsIVLimited</td><td>12,463,665.67</td><td>6,821,402.63</td><td>78,910.32</td><td>19,206,157.98</td><td>-</td></tr><tr><td>SunriseCapitalHoldingsVLimited</td><td>4,047,689.40</td><td>5,364,712.83</td><td>750,200.50</td><td>8,662,201.73</td><td>-</td></tr><tr><td>中信标普指数信息服务(北京)有限公司</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>小计</td><td>16,512,405.32</td><td>12,186,115.46</td><td>829,115.89</td><td>27,869,404.89</td><td>-</td></tr><tr><td>合计</td><td>9,607,514,080.96</td><td>449,995,947.17</td><td>270,808,595.80</td><td>9,786,701,432.33</td><td>14,965,691.15</td></tr></table>
    """
    
    try:
        # 执行转换
        result = html_table_to_flattened(html_input)
        
        # 打印结果
        print("=" * 120)
        print("单元格级扁平化结果（共{}行）".format(len(result)))
        print("=" * 120)
        for idx, row in enumerate(result, 1):
            print(f"行{idx:2d}: {row}")
        
        # 保存结果到文件（方便后续构建向量库）
        output_file = "flattened_investment_table.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(result))
        
        print("\n" + "=" * 120)
        print(f"✅ 转换完成！结果已保存至: {output_file}")
        print("=" * 120)
        
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
