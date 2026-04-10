import pandas as pd
import glob
import os
import json

def research_datasets():
    # 프로젝트 루트 기준 검색
    files = glob.glob('firsteda/**/*.parquet', recursive=True) + glob.glob('firsteda/**/*.csv', recursive=True)
    
    results = {}
    
    for f in files:
        file_name = os.path.basename(f)
        print(f"Analyzing {file_name}...")
        try:
            if f.endswith('.parquet'):
                df = pd.read_parquet(f)
            else:
                df = pd.read_csv(f)
            
            info = {
                "path": f,
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "null_pct": (df.isnull().sum() / len(df) * 100).to_dict(),
                "unique_counts": df.nunique().to_dict(),
                "sample": df.head(3).to_dict(orient='records')
            }
            results[file_name] = info
        except Exception as e:
            results[file_name] = {"error": str(e)}
            
    with open('research_results.json', 'w', encoding='utf-8') as out:
        json.dump(results, out, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    research_datasets()
