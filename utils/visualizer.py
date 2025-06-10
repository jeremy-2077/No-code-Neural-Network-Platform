import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import seaborn as sns
import pandas as pd

def set_chinese_font():
    """设置matplotlib以支持中文显示"""
    try:
        # 尝试查找常见的中文字体
        fonts = ['PingFang SC', 'Microsoft YaHei', 'SimHei', 'Heiti TC', 'sans-serif']
        
        # 设置字体
        matplotlib.rcParams['font.sans-serif'] = fonts
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 验证字体是否设置成功
        prop = FontProperties(family=fonts)
        if 'not found' in prop.get_name().lower():
             print(f"警告：找不到任何指定的中文字体，图例可能仍然乱码。")
        else:
             print(f"成功设置中文字体: {prop.get_name()}")
             
    except Exception as e:
        print(f"设置中文字体时出错: {e}")

# 在模块加载时设置字体
set_chinese_font()


class DataVisualizer:
    def plot_data(self, figure, df: pd.DataFrame, plot_type: str,
                  x_col: str, y_col: str):
        ax = figure.add_subplot(111)
        
        try:
            # 检查列是否存在
            if x_col not in df.columns or y_col not in df.columns:
                ax.text(0.5, 0.5, f"找不到指定的列: {x_col} 或 {y_col}",
                        ha='center', va='center')
                return
            
            if plot_type == "折线图":
                df.plot(x=x_col, y=y_col, kind='line', ax=ax)
            elif plot_type == "柱状图":
                df.plot(x=x_col, y=y_col, kind='bar', ax=ax)
            elif plot_type == "散点图":
                df.plot(x=x_col, y=y_col, kind='scatter', ax=ax)
            elif plot_type == "箱线图":
                df.boxplot(column=y_col, by=x_col, ax=ax)
            elif plot_type == "相关性热图":
                # 计算相关性，只选择数值列
                numeric_df = df.select_dtypes(include=['number'])
                if numeric_df.empty:
                    ax.text(0.5, 0.5, "没有可计算相关性的数值数据", ha='center', va='center')
                    return
                sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', ax=ax)
            
            ax.set_title(f"{plot_type}: {x_col} vs {y_col}")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            
        except Exception as e:
            ax.text(0.5, 0.5, f"绘图错误: {str(e)}", ha='center', va='center')
        
        figure.tight_layout() 