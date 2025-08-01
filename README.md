# PostgreSQL DDL コメント抽出ツール

## 📌 用途
このツールは、PostgreSQL の DDL ファイル（.sql）から  
**テーブル名・カラム名の物理名と論理名**を自動で抽出し、  
**Excel で開ける CSV 形式**で出力する Python スクリプトです。
<br>


## ▶️ 使用方法
### ❗ 事前準備
- Python 3.x がインストールされていること
- `DDL/` フォルダ内に `.sql` ファイルを配置（※1ファイル = 1テーブルが前提）
### 🏃 実行コマンド
#### 方法①：引数なし（推奨）
```bash
python extract_ddl_info.py
```
この場合、`extract_ddl_info.py` と**同じ階層の `DDL/` フォルダ**が自動で対象になります。
#### 方法②：フォルダまたはファイルを引数で指定
```bash
python extract_ddl_info.py ./my_sql_folder/
```
<br>

## 📂 フォルダ構成（推奨）
```bash
project/
├── extract_ddl_info.py        # このスクリプト本体
├── DDL/                       # ← SQLファイルを格納するフォルダ
│   ├── sample_table.sql
│   └── another_table.sql
├── result/                    # ← 自動生成される出力フォルダ
│   └── core_sample_table_サンプルテーブル_20250801164200.csv
```
<br>

## 📝 出力ファイル内容（CSV）

CSVファイルの構成は以下のようになります：
```
1行目   : スキーマ名
2行目   : テーブル物理名, テーブル論理名
3行目   : （空行）
4行目   : No, 物理名, 論理名
5行目～ : カラム情報（DDL内のコメント記述順）
```

### 例：
```csv
core
sample_table,サンプルテーブル

No,物理名,論理名
1,sample_column,サンプルカラム
2,name,名前
```
<br>

## 📄 出力ファイル名の形式
CSVファイル名は以下の形式で出力されます：

```
【スキーマ名】_【テーブル物理名】_【テーブル論理名】_【日時（yyyymmddhhmmss）】.csv
```

### 例：

```
core_sample_table_サンプルテーブル_20250801170000.csv
```

> ファイル名に使えない文字（`/ \ : * ? " < > |`）は、自動的にアンダースコア（`_`）に置換されます。

---
<br>

## ⚠️ 注意点

* DDLファイル内に以下の形式のコメントが必要です：

```sql
COMMENT ON TABLE schema.table_name IS 'テーブル論理名';
COMMENT ON COLUMN schema.table_name.column_name IS 'カラム論理名';
```

* 出力されるカラムの順序は、`COMMENT ON COLUMN` の記述順です（`CREATE TABLE` の定義順ではありません）。
* 1つの `.sql` ファイルに1テーブル分の情報のみ含めてください。
* 出力ファイルは UTF-8 (BOM付き) で書き出されるため、**Excelで文字化けせずに開くことができます。**

<br>

## 📮 ライセンス

このスクリプトは個人・業務利用問わず自由に使用・改変可能です。
商用利用、再配布も可能ですが、自己責任でご利用ください。
