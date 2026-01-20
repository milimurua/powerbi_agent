Flujo Excel a BigQuery

El proceso de ingesta sigue los siguientes pasos:

Lectura de un archivo Excel (.xlsx) con múltiples hojas

Exportación de cada hoja a un archivo CSV independiente

Generación automática de esquemas de BigQuery con todas las columnas como STRING

Carga de cada CSV como una tabla en BigQuery

Excel (.xlsx)
Hoja A → CSV → Tabla BigQuery
Hoja B → CSV → Tabla BigQuery
Hoja C → CSV → Tabla BigQuery

Requisitos

Docker

Bash (Linux / WSL / macOS)

Google Cloud CLI

BigQuery habilitado en el proyecto destino

Permisos para crear y reemplazar tablas en BigQuery

Paso 1 – Convertir Excel a CSV

Dado un archivo Excel con múltiples hojas, el siguiente comando:

Lee todas las hojas

Normaliza los nombres

Genera un CSV por hoja

Fuerza todos los valores a texto para evitar conflictos de tipado

docker run --rm -it \
  -v "$(pwd)":/work -w /work \
  python:3.12-slim \
  bash -lc "pip install -q pandas openpyxl && python -c \"import pandas as pd, pathlib, re; xlsx='tablas_powerbi.xlsx'; out=pathlib.Path('out_csv'); out.mkdir(exist_ok=True); xl=pd.ExcelFile(xlsx, engine='openpyxl'); san=lambda s: re.sub(r'[^A-Za-z0-9_\\-]+','',re.sub(r'\\s+','_',s.strip())) or 'sheet'; \
[ (pd.read_excel(xl, sheet_name=sh, dtype=str).fillna('').to_csv(out / f'{pathlib.Path(xlsx).stem}__{san(sh)}.csv', index=False, encoding='utf-8', lineterminator='\\n'), print('Wrote', out / f'{pathlib.Path(xlsx).stem}__{san(sh)}.csv')) for sh in xl.sheet_names ]\""


La estructura generada es:

out_csv/
├── tablas_powerbi__hoja_a.csv
├── tablas_powerbi__hoja_b.csv
├── tablas_powerbi__hoja_c.csv

Paso 2 – Configurar Google Cloud CLI
Instalar Google Cloud CLI usando Snap
sudo apt update
sudo apt install -y snapd
sudo snap install google-cloud-cli --classic


En entornos WSL es necesario cerrar y volver a abrir la terminal.

Verificar la instalación
gcloud --version
bq version

Autenticarse
gcloud auth login

Seleccionar el proyecto
gcloud config set project <id-del-proyecto>

Verificar acceso a BigQuery
bq ls

Paso 3 – Carga de CSVs en BigQuery

El repositorio incluye un script que:

Recorre todos los CSV generados

Crea automáticamente un esquema JSON por tabla (todas las columnas como STRING)

Normaliza nombres de tablas y columnas

Carga o reemplaza tablas en BigQuery

Script upload_to_bq.sh
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="id-del-proyecto"
DATASET="dataset_destino"
CSV_DIR="out_csv"
SCHEMA_DIR=".bq_schema"

mkdir -p "$SCHEMA_DIR"

sanitize () {
  local name="$1"
  name="$(echo "$name" | tr '[:upper:]' '[:lower:]')"
  name="$(echo "$name" | sed -E 's/[^a-z0-9_]+/_/g; s/^_+//; s/_+$//; s/__+/_/g')"
  [[ "$name" =~ ^[a-z_] ]] || name="t_${name}"
  [[ -n "$name" ]] || name="t_sheet"
  echo "$name"
}

make_schema_all_string () {
  local csv="$1"
  local schema_json="$2"

  local header
  header="$(head -n 1 "$csv")"

  python3 - <<PY "$header" "$schema_json"
import sys, json, csv, io, re

header = sys.argv[1]
out = sys.argv[2]

reader = csv.reader(io.StringIO(header))
cols = next(reader)

def clean(col):
    col = re.sub(r'\s+', '_', col.strip())
    col = re.sub(r'[^A-Za-z0-9_]+', '', col)
    if not col or not re.match(r'^[A-Za-z_]', col):
        col = f"f_{col}" if col else "f_col"
    return col

fields = [{"name": clean(c), "type": "STRING", "mode": "NULLABLE"} for c in cols]

with open(out, "w", encoding="utf-8") as f:
    json.dump(fields, f, ensure_ascii=False)
PY
}

shopt -s nullglob
files=("$CSV_DIR"/*.csv)

if (( ${#files[@]} == 0 )); then
  echo "No se encontraron archivos CSV en $CSV_DIR" >&2
  exit 1
fi

for f in "${files[@]}"; do
  base="$(basename "$f" .csv)"
  table="$(sanitize "$base")"
  dest="${PROJECT_ID}:${DATASET}.${table}"
  schema_file="${SCHEMA_DIR}/${table}.json"

  make_schema_all_string "$f" "$schema_file"

  bq load \
    --source_format=CSV \
    --schema="$schema_file" \
    --skip_leading_rows=1 \
    --replace \
    --max_bad_records=100 \
    "$dest" \
    "$f"
done

echo "Carga finalizada."


Dar permisos de ejecución y ejecutar:

chmod +x upload_to_bq.sh
./upload_to_bq.sh

Resultado

Se crea una tabla en BigQuery por cada hoja del Excel

Todas las columnas se cargan como STRING

Los nombres de tablas y columnas quedan normalizados

El proceso es idempotente y reproducible