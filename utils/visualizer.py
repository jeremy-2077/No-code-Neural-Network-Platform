import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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
                sns.heatmap(df.corr(), annot=True, cmap='coolwarm', ax=ax)
            
            ax.set_title(f"{plot_type}: {x_col} vs {y_col}")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            
        except Exception as e:
            ax.text(0.5, 0.5, f"绘图错误: {str(e)}", ha='center', va='center')
        
        figure.tight_layout() 