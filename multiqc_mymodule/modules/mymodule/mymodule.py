import csv, logging, os
from multiqc.modules.base_module import BaseMultiqcModule
try:
    from multiqc.modules.base_module import ModuleNoSamplesFound
except Exception:
    class ModuleNoSamplesFound(UserWarning): pass

log = logging.getLogger(__name__)

def _get(row, *keys):
    for k in keys:
        v = row.get(k)
        if v not in (None, ""):
            return v
    return None

class MultiqcModule(BaseMultiqcModule):
    def __init__(self):
        super(MultiqcModule, self).__init__(name="My Module", anchor="mymodule",
                                            info="Reads CSV (sample,metric,value), shows a table and a bar chart.")
        
        log.warning("[mymodule] Hello World - module initialised")

        data_by_sample = {}

        files = list(self.find_log_files("mymodule"))
        log.debug(f"mymodule: matched {len(files)} files: {[f.get('fn') for f in files]}")

        for f in files:
            fn = f.get("fn")
            root = f.get("root") or ""
            fullpath = fn if os.path.isabs(fn) else os.path.join(root, fn)
            try:
                with open(fullpath, "r", encoding="utf-8", errors="replace", newline="") as fh:
                    head = fh.read(4096); fh.seek(0)
                    try:
                        dialect = csv.Sniffer().sniff(head, delimiters=",\t;")
                        delim = dialect.delimiter
                    except Exception:
                        delim = ","
                    reader = csv.DictReader(fh, delimiter=delim)
                    for row in reader:
                        if not row: continue
                        s = _get(row, "sample", "Sample", "SAMPLE") or os.path.basename(os.path.dirname(fullpath)) or "sample"
                        metric = _get(row, "metric", "Metric", "METRIC")
                        val_raw = _get(row, "value", "Value", "VALUE")
                        if metric is None or val_raw is None: continue
                        try:
                            val = float(str(val_raw).strip())
                        except Exception:
                            continue
                        data_by_sample.setdefault(s, {})[metric] = val
            except Exception as e:
                log.warning(f"mymodule: failed to read {fullpath}: {e}")

        data_by_sample = self.ignore_samples(data_by_sample)
        if not data_by_sample:
            log.debug("mymodule: no usable rows found; skipping module.")
            raise ModuleNoSamplesFound("mymodule: no data")

        from multiqc.plots import table, bargraph
        headers = {}
        for mset in data_by_sample.values():
            for m in mset.keys():
                headers.setdefault(m, {"title": m, "format": "{:.3f}"})

        self.add_section(
            name="Parsed CSV (Table)",
            anchor="mymodule_table",
            plot=table.plot(data_by_sample, headers=headers)
        )

        eff = {s: {"efficiency": m["efficiency"]} for s, m in data_by_sample.items() if "efficiency" in m}
        if eff:
             self.add_section(
                name="efficiency",
                anchor="mymodule_eff",
                plot=bargraph.plot(eff, pconfig={"id": "mymodule_eff", "ylab": "efficiency", "cpswitch": False})
            )

        dor = {s: {"drop-out-rate": m["drop-out-rate"]} for s, m in data_by_sample.items() if "drop-out-rate" in m}
        if dor: 
            self.add_section(
                name="drop-out-rate",
                anchor="mymodule_dor",
                plot=bargraph.plot(dor, pconfig={"id": "mymodule_dor", "ylab": "drop-out-rate", "cpswitch":False})
            )
  

