import os
import re
import csv
from pathlib import Path
from datetime import datetime

# ファイル名に使用できない文字をアンダースコアに置換する関数
def sanitize_filename(s):
    # WindowsなどのOSで使用できない文字（\, /, :, *, ?, ", <, >, |）をすべてアンダースコアに置換
    return re.sub(r'[\\/:*?"<>|]', '_', s)

# SQLテキストから「COMMENT ON TABLE」文を抽出し、スキーマ・テーブル物理名・論理名を取得する関数
def extract_table_info(sql_text):
    pattern = re.compile(
        r"COMMENT\s+ON\s+TABLE\s+([\w]+)\.([\w]+)\s+IS\s+'([^']+)'", re.IGNORECASE)
    match = pattern.search(sql_text)
    if match:
        schema, table_name, logical_name = match.groups()
        return schema, table_name, logical_name
    return None, None, None  # テーブル情報が見つからなかった場合

# SQLテキストから「COMMENT ON COLUMN」文を抽出し、カラムの物理名と論理名の一覧を取得する関数
def extract_column_info(sql_text, schema, table_name):
    # カラム情報を順番通りに抽出するために finditer を使用
    pattern = re.compile(
        rf"COMMENT\s+ON\s+COLUMN\s+{schema}\.{table_name}\.([\w]+)\s+IS\s+'([^']+)'", re.IGNORECASE)
    return [(m.group(1), m.group(2)) for m in pattern.finditer(sql_text)]

# SQLファイルを1つ読み込んで、テーブル情報＋カラム情報をまとめて返す関数
def process_sql_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        sql_text = f.read()

    schema, table_name, table_logical_name = extract_table_info(sql_text)
    if not table_name:
        return None  # テーブル情報が存在しなければスキップ

    column_infos = extract_column_info(sql_text, schema, table_name)
    return {
        "schema": schema,
        "table_name": table_name,
        "table_logical_name": table_logical_name,
        "columns": column_infos
    }

# 出力先フォルダに1ファイルずつCSVを書き出す関数（指定フォーマットに対応）
def write_custom_csv(result, output_dir):
    # 出力フォルダを作成（すでに存在している場合は何もしない）
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # ファイル名に追加するタイムスタンプ（例：20250801161530）
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # ファイル名を構成：schema_table_論理名_タイムスタンプ.csv
    schema = result['schema']
    table_name = result['table_name']
    logical_name_sanitized = sanitize_filename(result['table_logical_name'])

    filename = f"{schema}_{table_name}_{logical_name_sanitized}_{timestamp}.csv"
    output_path = output_dir_path / filename

    # CSVファイル書き出し（UTF-8 BOM付きでExcel対応）
    with open(output_path, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        # 1行目：スキーマ名
        writer.writerow([schema])

        # 2行目：テーブル物理名・論理名
        writer.writerow([table_name, result["table_logical_name"]])

        # 3行目：空行
        writer.writerow([])

        # 4行目：カラムのヘッダ
        writer.writerow(['No', '物理名', '論理名'])

        # 5行目以降：カラム情報（定義順に出力）
        for idx, (col_name, col_logical) in enumerate(result["columns"], 1):
            writer.writerow([idx, col_name, col_logical])

    print(f"✅ 出力完了: {output_path.name}")

# フォルダまたはファイルから .sql ファイルを取得する関数
def get_sql_files(input_path):
    path = Path(input_path)
    if path.is_dir():
        return list(path.glob('*.sql'))  # ディレクトリなら全.sqlファイルを対象
    elif path.is_file() and path.suffix == '.sql':
        return [path]  # 単一ファイル指定時
    else:
        return []

# メイン処理：ファイルを処理してresultフォルダへ出力
def main(input_path):
    sql_files = get_sql_files(input_path)

    # Pythonファイルと同じ階層に result フォルダを作成して出力
    result_dir = Path(__file__).parent / 'result'

    for file in sql_files:
        result = process_sql_file(file)
        if result:
            write_custom_csv(result, result_dir)
        else:
            print(f"⚠️ スキップ: {file.name}（テーブル情報が見つかりません）")

# スクリプトのエントリーポイント
if __name__ == '__main__':
    import sys

    # 引数が指定されていなければ ./DDL フォルダを使う
    if len(sys.argv) < 2:
        default_path = Path(__file__).parent / 'DDL'
        if default_path.exists() and default_path.is_dir():
            print(f"ℹ️ 入力パス未指定のため、デフォルトの DDL フォルダを使用します: {default_path}")
            main(default_path)
        else:
            print("❌ 入力パスが指定されておらず、'DDL' フォルダも見つかりません。")
            print("💡 対応策: DDL フォルダを作成するか、引数でパスを指定してください。")
    else:
        main(sys.argv[1])
