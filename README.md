# MultiQC-plugin
A simple **MultiQC plugin** that discovers Duplex QC CSV outputs, parses
`sample,metric,value`, and adds:
- a Parsed CSV (Table) section, and
- bar charts for metrics (**Efficiency**, **Drop-out Rate**).

Tested with **MultiQC v1.14**.

---

## Quick start

```bash
# 1) clone & enter
git clone https://github.com/<you>/multiqc-mymodule.git
cd multiqc-mymodule

# 2) create a clean env (venv example)
python3 -m venv .venv1p14
source .venv1p14/bin/activate

# 3) install MultiQC and this plugin (editable for dev)
pip install "multiqc==1.14.*"
pip install -e .

# 4) run on example data
multiqc -v -f \
  --cl-config 'sp: { mymodule: { fn: "*.[ct]sv" } }' \
  -m mymodule test_data -o _report

open _report/multiqc_report.html   
