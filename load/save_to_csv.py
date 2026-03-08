from pathlib import Path


def save_data(df):
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "premium_analysis.csv"
    df.to_csv(output_path, index=False)

    print(f"資料已儲存到: {output_path}")