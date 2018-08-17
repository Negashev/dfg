import os

from apscheduler.triggers.cron import CronTrigger
from japronto import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiodocker

DFG_URL_CLONE = os.environ['DFG_URL_CLONE']
DFG_PATH_DOCKERFILE = os.getenv('DFG_PATH_DOCKERFILE', 'Dockerfile')
DFG_IMAGE_TAG = os.environ['DFG_IMAGE_TAG']
DFG_AUTH_BASE64 = os.getenv('DFG_AUTH_BASE64', None)

async def logging(data):
    sha256 = None
    async for item in data:
        if 'stream' in item:
            if item['stream'] != '\n':
                print(item['stream'].rstrip())
        elif 'status' in item:
            print(item['status'])
        elif 'aux' in item:
            if 'ID'in item['aux']:
                sha256 = item['aux']['ID']
                print(sha256)
            if 'Digest'in item['aux']:
                sha256 = item['aux']['Digest']
                print(sha256)
        elif 'error' in item:
            print(item['error'])
        else:
            print(item)
    return sha256


async def build_from_git():
    try:
        repo_url = DFG_URL_CLONE.split('@')[-1]
        print(f"Clone git {repo_url}")
    except Exception as e:
        pass
    docker = aiodocker.Docker()
    build = await docker.images.build(
        remote=DFG_URL_CLONE,
        path_dockerfile=DFG_PATH_DOCKERFILE,
        tag=DFG_IMAGE_TAG,
        quiet=False,
        buildargs=dict(**os.environ),
        nocache=True,
        pull=True,
        rm=True,
        forcerm=False,
        labels=None,
        stream=True
    )

    await logging(build)
    push = await docker.images.push(DFG_IMAGE_TAG, auth=DFG_AUTH_BASE64, stream=True)
    await logging(push)
    await docker.close()


async def connect_scheduler():
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(build_from_git, CronTrigger.from_crontab(os.getenv('DFG_CRON', '* * * * *')), max_instances=1)
    scheduler.start()


async def index(request):
    return request.Response(json='ok')


app = Application()
if 'DFG_BUILD_ON_START' in os.environ:
    app.loop.run_until_complete(build_from_git())
app.loop.run_until_complete(connect_scheduler())
router = app.router
router.add_route('/', index)
app.run(host='0.0.0.0', port=8080, debug=True)