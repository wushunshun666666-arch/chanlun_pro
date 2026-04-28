from fastapi import APIRouter
from ..tasks.scheduler import run_manual_scan

router = APIRouter()

@router.post('/scan')
def manual_scan():
    job = run_manual_scan()
    return {'status': 'started', 'task_id': str(job)}
