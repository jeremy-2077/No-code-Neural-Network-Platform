import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif

class DataProcessor:
    def __init__(self):
        self.scaler = None
        self.pca = None
        
    def process_data(self, df: pd.DataFrame, normalize_method: str,
                    missing_method: str, feature_method: str) -> pd.DataFrame:
        try:
            # 复制数据框以避免修改原始数据
            processed_df = df.copy()
            
            # 处理缺失值
            if missing_method == "删除":
                processed_df = processed_df.dropna()
            elif missing_method == "均值填充":
                processed_df = processed_df.fillna(processed_df.mean())
            elif missing_method == "中位数填充":
                processed_df = processed_df.fillna(processed_df.median())
            
            # 数据标准化/归一化
            numeric_columns = processed_df.select_dtypes(include=['float64', 'int64']).columns
            if normalize_method == "标准化":
                self.scaler = StandardScaler()
                processed_df[numeric_columns] = self.scaler.fit_transform(processed_df[numeric_columns])
            elif normalize_method == "归一化":
                self.scaler = Normalizer()
                processed_df[numeric_columns] = self.scaler.fit_transform(processed_df[numeric_columns])
            elif normalize_method == "最大最小缩放":
                self.scaler = MinMaxScaler()
                processed_df[numeric_columns] = self.scaler.fit_transform(processed_df[numeric_columns])
            
            # 特征工程
            if feature_method == "主成分分析(PCA)":
                if len(numeric_columns) > 0:  # 确保有数值列
                    self.pca = PCA(n_components=min(5, len(numeric_columns)))
                    pca_result = self.pca.fit_transform(processed_df[numeric_columns])
                    pca_df = pd.DataFrame(
                        pca_result,
                        columns=[f'PC{i+1}' for i in range(pca_result.shape[1])]
                    )
                    # 保留非数值列
                    non_numeric_cols = processed_df.select_dtypes(exclude=['float64', 'int64']).columns
                    if len(non_numeric_cols) > 0:
                        processed_df = pd.concat([processed_df[non_numeric_cols], pca_df], axis=1)
                    else:
                        processed_df = pca_df
            
            elif feature_method == "特征选择":
                if len(numeric_columns) > 1:  # 确保有足够的特征
                    selector = SelectKBest(score_func=f_classif, k=min(5, len(numeric_columns)))
                    selected_features = selector.fit_transform(
                        processed_df[numeric_columns],
                        processed_df[numeric_columns].iloc[:, 0]  # 使用第一列作为目标变量
                    )
                    selected_columns = numeric_columns[selector.get_support()].tolist()
                    processed_df = processed_df[selected_columns]
            
            return processed_df
            
        except Exception as e:
            raise Exception(f"数据处理错误: {str(e)}") 