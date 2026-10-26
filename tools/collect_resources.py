"""Extract a small, public numerical record from the existing resource study.

Usage: python tools/collect_resources.py --source /path/to/results.json
This only reads historical results. It does not run an electromagnetic solver.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    args = ap.parse_args()
    raw = Path(args.source).read_bytes()
    src = json.loads(raw.decode('utf-8-sig'))
    hw = src['hardware_snapshot']
    result = {
        'schema_version': 1,
        'assembled_date': '2026-10-26',
        'source_project_relative_path': 'AH53_FDTD_RunStudy/results.json',
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'original_generated_at_hong_kong': src['generated_at_hong_kong'],
        'note': 'Historical evidence only. Checker estimates and 100 fs pilots are not optical convergence or position-accuracy validation.',
        'hardware_snapshot': {k: hw[k] for k in ('cpu','physical_cores','logical_processors','ram_total_bytes','gpu','gpu_memory_total_mib')},
        'setup': {'wavelength_nm':532,'geometry':'QEM45 from independently imported VDATA','illumination':'Gaussian, waist 3 um, normal -Z, X polarization','domain_um':[15.2,27.2,3.3],'solver':'Lumerical CPU, 8 threads','target_max_time_ps':1,'optical_convergence_verified':False},
        'cases': [], 'pilots': []
    }
    for c in src['cases']:
        result['cases'].append({
            'case': c['case'], 'requested_step_nm':c['requested_step_nm'], 'graded':c['graded'],
            'classification':'checker_estimate', 'recommended_bytes':c['recommended_memory']['bytes'],
            'yee_nodes_million':c['yee_nodes_million'], 'dt_fs':c['dt_fs'],
            'runtime_classification':c['runtime']['classification'],
            'same_grid_1ps_wall_seconds_estimate':c['runtime'].get('prediction',{}).get('total_wall_seconds_estimate'),
            'cross_grid_propagation_seconds_range':c['runtime'].get('propagation_seconds_range'),
            'actual_full_1ps_run':False, 'optical_convergence_verified':False
        })
    for b in src['benchmarks']:
        result['pilots'].append({
            'case':b['case'],'classification':'actual_short_pilot','physical_time_fs':b['completed_simulation_time_seconds']*1e15,
            'wall_seconds':b['elapsed_wall_seconds'],'peak_engine_reported_bytes':b['largest_engine_reported_peak_memory']['bytes'],
            'peak_label':b['largest_engine_reported_peak_memory']['label'],
            'initialization_seconds':b['wall_seconds_actual']['initialization'],
            'solve_seconds':b['wall_seconds_actual']['solve'],'clean_completed':b['clean_completed'],
            'optical_convergence_verified':b['optical_convergence_verified']
        })
    out=ROOT/'evidence'/'resource_metrics.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Extracted {} checker cases and {} pilots'.format(len(result['cases']),len(result['pilots'])))

if __name__=='__main__':main()
